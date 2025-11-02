import httpx
from app.core.config import settings
import logging
import json
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Kill chain stages for normalization
KILLCHAIN_STAGES = [
    "Reconnaissance",
    "Weaponization",
    "Delivery",
    "Exploitation",
    "Installation",
    "Command & Control (C2)",
    "Actions on Objectives"
]

def _is_generic(label: str) -> bool:
    """Detect fallback-style generic labels."""
    generic = ["Food Prices Rise", "Civil Unrest Increases", "Crop Yields", "Drought"]
    return any(g.lower() in label.lower() for g in generic)

def _contains_generic_nodes(nodes):
    """Check if nodes contain generic fallback patterns."""
    return any(_is_generic(n.get("label", "")) for n in nodes or [])

def _build_prompt(user_prompt: str, stage_configs: dict = None) -> str:
    """Construct strict JSON-only Groq prompt."""
    stage_config_str = json.dumps(stage_configs, indent=2) if stage_configs else "{}"
    
    return f"""You are an expert forecasting analyst. Create a Dynamic Bayesian Network (DBN) from the user's scenario description below.

REQUIREMENTS:
1. Output MUST be valid JSON, no markdown or prose.
2. Generate 3–8 UNIQUE, CONTEXT-SPECIFIC nodes derived directly from the prompt.
3. Each node must include: id, label, domain, stage, impact (0.0-1.0), confidence (0.0-1.0).
4. Domains: Environment, Economy, Society, Policy, Technology.
5. Stages: Reconnaissance, Weaponization, Delivery, Exploitation, Installation, Command & Control (C2), Actions on Objectives.
6. Include 2–6 causal edges with source, target, stage_transition (format "Stage1→Stage2" using →), strength_hint (0-1), llm_confidence (0-1).
7. Do NOT use generic or placeholder nodes like "Food Prices Rise" or "Civil Unrest Increases".
8. Reflect only the entities actually implied by the user scenario.

Example for the prompt "What if an AI becomes president?":
{{
  "stage": "Exploitation",
  "nodes": [
    {{"id": "TEC_01", "label": "AI Leadership", "domain": "Technology", "stage": "Delivery", "impact": 0.8, "confidence": 0.85}},
    {{"id": "POL_01", "label": "Automated Governance", "domain": "Policy", "stage": "Exploitation", "impact": 0.7, "confidence": 0.75}},
    {{"id": "SOC_01", "label": "Public Trust in AI", "domain": "Society", "stage": "Delivery", "impact": 0.6, "confidence": 0.7}}
  ],
  "edges": [
    {{"source": "TEC_01", "target": "POL_01", "stage_transition": "Delivery→Exploitation", "strength_hint": 0.65, "llm_confidence": 0.8}},
    {{"source": "POL_01", "target": "SOC_01", "stage_transition": "Exploitation→Delivery", "strength_hint": 0.55, "llm_confidence": 0.7}}
  ]
}}

User prompt: {user_prompt}

Stage Configurations:
{stage_config_str}

Return ONLY valid JSON."""

async def get_llama_forecast(prompt: str, stage_configs: dict = None) -> dict:
    """Send scenario prompt to Groq LLaMA-3 and normalize response."""
    
    # Log the received prompt
    logger.info(f"🟡 [LLAMA_CLIENT] get_llama_forecast called with prompt: '{prompt}'")
    logger.info(f"🟡 [LLAMA_CLIENT] LLAMA_API_URL: {settings.LLAMA_API_URL}")
    logger.info(f"🟡 [LLAMA_CLIENT] LLAMA_MODEL: {settings.LLAMA_MODEL}")
    
    # Check if API key is set
    if not settings.LLAMA_API_KEY:
        logger.warning("⚠️ LLAMA_API_KEY not set, using mock response")
        return _get_mock_response()
    
    # Check if we should use mock endpoint
    if settings.LLAMA_API_URL == "http://localhost:8000/mock-llama":
        logger.warning("⚠️ Using mock LLAMA response (default endpoint)")
        return _get_mock_response()
    
    headers = {
        "Authorization": f"Bearer {settings.LLAMA_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.LLAMA_MODEL or "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": "You output Dynamic Bayesian Network structures in JSON only."},
            {"role": "user", "content": _build_prompt(prompt, stage_configs)},
        ],
        "temperature": 0.8,
        "top_p": 0.9,
        "max_tokens": 2000,
        "response_format": {"type": "json_object"}  # Request JSON response
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            logger.info(f"🟠 [GROQ] Sending prompt to Groq API")
            logger.info(f"🟠 [GROQ] URL: {settings.LLAMA_API_URL}")
            logger.info(f"🟠 [GROQ] Model: {payload['model']}")
            logger.info(f"🟠 [GROQ] User prompt: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'")
            
            r = await client.post(settings.LLAMA_API_URL, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
            content = data["choices"][0]["message"]["content"]
            
            logger.info(f"🔴 [GROQ RESPONSE] Received response, status: {r.status_code}")
            logger.info(f"🔴 [GROQ RESPONSE] Raw response preview (first 300 chars): {content[:300]}")
            
    except Exception as e:
        logger.warning(f"Groq API request failed: {e}", exc_info=True)
        return {"stage": "Error", "nodes": [], "edges": [], "using_fallback": True}

    # Try to parse JSON
    parsed = None
    try:
        parsed = json.loads(content)
        logger.info("✅ [GROQ RESPONSE] Successfully parsed JSON from Groq response")
    except json.JSONDecodeError:
        logger.warning("Direct JSON parsing failed, trying regex extraction")
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
                logger.info("✅ [GROQ RESPONSE] Successfully extracted JSON using regex fallback")
            except json.JSONDecodeError as e2:
                logger.error(f"Regex extraction also failed: {e2}")
        else:
            logger.warning("No JSON object found in Groq response")
            logger.debug(f"Response content (first 500 chars): {content[:500]}")
    
    if not parsed:
        logger.warning("❗ No valid JSON; returning empty structure.")
        return {"stage": "Error", "nodes": [], "edges": [], "using_fallback": True}

    # Normalize the response
    normalized = normalize_llm_spec(parsed)
    
    # Log parsed node information
    logger.info(f"✅ [GROQ RESPONSE] Parsed nodes count: {len(normalized.get('nodes', []))}")
    logger.info(f"✅ [GROQ RESPONSE] Parsed edges count: {len(normalized.get('edges', []))}")
    node_labels = [n.get('label', 'N/A') for n in normalized.get('nodes', [])[:5]]
    logger.info(f"✅ [GROQ RESPONSE] First 5 node labels: {node_labels}")

    # Detect generic fallback pattern and retry once if detected
    if _contains_generic_nodes(normalized.get("nodes")):
        logger.warning("⚠️ Generic fallback detected; retrying once with higher temperature.")
        
        # Retry once with slightly higher temperature
        payload["temperature"] = 0.9
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                logger.info("🟠 [GROQ RETRY] Retrying with temperature 0.9")
                r = await client.post(settings.LLAMA_API_URL, json=payload, headers=headers)
                r.raise_for_status()
                data = r.json()
                content = data["choices"][0]["message"]["content"]
                
                # Parse retry response
                try:
                    parsed = json.loads(content)
                except json.JSONDecodeError:
                    match = re.search(r"\{.*\}", content, re.DOTALL)
                    if match:
                        parsed = json.loads(match.group(0))
                
                if parsed:
                    normalized = normalize_llm_spec(parsed)
                    node_labels_retry = [n.get('label', 'N/A') for n in normalized.get('nodes', [])[:5]]
                    logger.info(f"✅ [GROQ RETRY] Retry node labels: {node_labels_retry}")
                    
                    # Check if retry still has generic nodes
                    if _contains_generic_nodes(normalized.get("nodes")):
                        logger.warning("⚠️ Retry still returned generic nodes; using result anyway.")
                    else:
                        logger.info("✅ [GROQ RETRY] Retry succeeded with unique nodes")
        except Exception as e:
            logger.warning(f"Retry failed: {e}")

    logger.info(f"✅ [GROQ RESPONSE] Final normalized nodes: {[n.get('label', 'N/A') for n in normalized.get('nodes', [])]}")
    normalized["using_fallback"] = False
    return normalized

def normalize_llm_spec(raw: dict) -> dict:
    """
    Convert LLM output into the DBN engine's expected shape:
    - edges[].stage_transition (Unicode arrow)
    - edges[].strength_hint, edges[].llm_confidence
    - nodes[].stage
    """
    if not isinstance(raw, dict):
        logger.error(f"normalize_llm_spec: raw input is not a dict, got {type(raw)}")
        return {"nodes": [], "edges": []}
    
    out = {"nodes": [], "edges": []}
    nodes = raw.get("nodes", [])
    edges = raw.get("edges", [])
    
    if not isinstance(nodes, list):
        logger.warning(f"normalize_llm_spec: nodes is not a list, got {type(nodes)}, using empty list")
        nodes = []
    if not isinstance(edges, list):
        logger.warning(f"normalize_llm_spec: edges is not a list, got {type(edges)}, using empty list")
        edges = []

    # Normalize nodes
    for idx, n in enumerate(nodes):
        if not isinstance(n, dict):
            logger.warning(f"normalize_llm_spec: node at index {idx} is not a dict, skipping")
            continue
            
        try:
            node_id = n.get("id")
            if not node_id:
                label = n.get("label", f"NODE_{idx}")
                if not isinstance(label, str):
                    label = str(label)
                node_id = label.upper().replace(" ", "_").replace("-", "_")
            
            if not isinstance(node_id, str):
                node_id = str(node_id)
            
            out["nodes"].append({
                "id": node_id,
                "label": str(n.get("label", f"Node {idx}")),
                "domain": str(n.get("domain", "Environment")),
                "stage": str(n.get("stage") or "Reconnaissance"),  # default; backfilled below from edges
                "state_type": "discrete",
                "state_space": ["low", "med", "high"],
            })
        except Exception as e:
            logger.warning(f"normalize_llm_spec: failed to normalize node at index {idx}: {e}")
            continue

    # Index
    node_by_id = {n["id"]: n for n in out["nodes"]}

    # Normalize edges
    for idx, e in enumerate(edges):
        if not isinstance(e, dict):
            logger.warning(f"normalize_llm_spec: edge at index {idx} is not a dict, skipping")
            continue
            
        try:
            st = e.get("stage_transition", "")
            if isinstance(st, str):
                st = st.replace("->", "→")  # ASCII to Unicode
            else:
                st = ""

            # Safely convert numeric values
            strength_hint = e.get("strength_hint") or e.get("strength") or 0.6
            llm_confidence = e.get("llm_confidence") or e.get("confidence") or 0.7
            
            try:
                strength_hint = float(strength_hint)
            except (ValueError, TypeError):
                strength_hint = 0.6
                
            try:
                llm_confidence = float(llm_confidence)
            except (ValueError, TypeError):
                llm_confidence = 0.7

            source = e.get("source")
            target = e.get("target")
            
            if not source or not target:
                logger.warning(f"normalize_llm_spec: edge at index {idx} missing source or target, skipping")
                continue

            edge = {
                "source": str(source),
                "target": str(target),
                "stage_transition": st or "",  # may fill below
                "strength_hint": strength_hint,
                "llm_confidence": llm_confidence,
            }
            out["edges"].append(edge)
        except Exception as e:
            logger.warning(f"normalize_llm_spec: failed to normalize edge at index {idx}: {e}")
            continue

    # Backfill node stages from edge transitions if missing or defaulted
    for e in out["edges"]:
        st = e.get("stage_transition", "")
        if "→" in st:
            a, b = st.split("→", 1)
            a = a.strip()
            b = b.strip()
            if e["source"] in node_by_id:
                current_stage = node_by_id[e["source"]].get("stage")
                if not current_stage or current_stage == "Reconnaissance":
                    node_by_id[e["source"]]["stage"] = a
            if e["target"] in node_by_id:
                current_stage = node_by_id[e["target"]].get("stage")
                if not current_stage or current_stage == "Reconnaissance":
                    node_by_id[e["target"]]["stage"] = b

    # Default transitions if still missing (first hop)
    for e in out["edges"]:
        if not e["stage_transition"]:
            src_stage = node_by_id.get(e["source"], {}).get("stage", "Reconnaissance")
            try:
                idx = KILLCHAIN_STAGES.index(src_stage)
            except ValueError:
                idx = 0
            a, b = KILLCHAIN_STAGES[idx], KILLCHAIN_STAGES[min(idx+1, len(KILLCHAIN_STAGES)-1)]
            e["stage_transition"] = f"{a}→{b}"

    return out

def _get_mock_response() -> dict:
    """Deterministic mock response for development/testing."""
    return {
        "stage": "Exploitation",
        "nodes": [
            {"id":"ECO_04","label":"Food Prices Rise","impact":0.23,"confidence":0.74,"domain":"Economy","stage":"Weaponization"},
            {"id":"SOC_02","label":"Civil Unrest Increases","impact":0.15,"confidence":0.68,"domain":"Society","stage":"Delivery"}
        ],
        "edges": [
            {"source":"ECO_04","target":"SOC_02","sign":"+","strength":0.6,"stage_transition":"Weaponization→Delivery"}
        ]
    }

async def llm_extract_entities(sentences: list[dict]) -> list[dict]:
    """Optional LLM-based entity extraction. If LLAMA_API_URL is mock, return []."""
    if settings.LLAMA_API_URL == "http://localhost:8000/mock-llama":
        return []
    payload = {"task":"extract_entities", "sentences":[s.get("text","") for s in sentences]}
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            r = await client.post(settings.LLAMA_API_URL, json=payload)
            r.raise_for_status()
            return r.json().get("entities", [])
        except Exception as e:
            logger.warning("LLM entity extraction failed: %s", e)
            return []

async def llm_extract_relations(sentences: list[dict]) -> list[dict]:
    if settings.LLAMA_API_URL == "http://localhost:8000/mock-llama":
        return []
    payload = {"task":"extract_relations", "sentences":[s.get("text","") for s in sentences]}
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            r = await client.post(settings.LLAMA_API_URL, json=payload)
            r.raise_for_status()
            return r.json().get("relations", [])
        except Exception as e:
            logger.warning("LLM relation extraction failed: %s", e)
            return []
