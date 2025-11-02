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

async def get_llama_forecast(prompt: str, stage_configs: dict) -> dict:
    """Send prompt to Groq LLaMA API and parse JSON response."""
    
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
    
    # Build the improved system prompt with context-specific instructions
    system_prompt = """You are an expert forecasting analyst that creates Dynamic Bayesian Network (DBN) structures from scenario descriptions.

CRITICAL: You must generate UNIQUE, CONTEXT-SPECIFIC nodes based ONLY on the user's prompt. DO NOT reuse example nodes or generic patterns from previous requests.

Your task: Analyze the user's scenario prompt and extract the SPECIFIC entities, events, and causal relationships mentioned. Create nodes and edges that reflect ONLY the ACTUAL content of their prompt.

Kill chain stages (in order):
["Reconnaissance","Weaponization","Delivery","Exploitation","Installation","Command & Control (C2)","Actions on Objectives"]

Domain categories:
- Economy: markets, prices, GDP, trade, inflation, employment, currency, investments
- Environment: climate, weather, natural disasters, resources, pollution, sustainability
- Society: population, health, migration, education, social unrest, demographics
- Policy: regulations, laws, government actions, subsidies, taxes, international relations
- Technology: innovation, infrastructure, automation, digital services, cybersecurity

Required JSON format:
{
  "stage": "string (one of the kill chain stages - choose the most relevant starting stage)",
  "nodes": [
    {
      "id": "string (unique identifier like ENV_01, ECO_02, SOC_03, POL_04, TEC_05)",
      "label": "string (specific name extracted from the user's scenario, e.g., 'Renewable Energy Adoption' not 'Energy')",
      "domain": "string (Economy, Society, Environment, Policy, or Technology)",
      "stage": "string (one of the kill chain stages above - REQUIRED)",
      "impact": 0.0-1.0,
      "confidence": 0.0-1.0
    }
  ],
  "edges": [
    {
      "source": "node_id",
      "target": "node_id",
      "sign": "+" or "-",
      "strength": 0.0-1.0,
      "stage_transition": "Reconnaissance→Weaponization" (REQUIRED - use Unicode arrow →, not ->),
      "strength_hint": 0.0-1.0,
      "llm_confidence": 0.0-1.0
    }
  ]
}

MANDATORY Rules:
1. EXTRACT UNIQUE ENTITIES directly from the user's prompt - read their words carefully and create nodes that match their specific scenario
2. DO NOT reuse labels like "Food Prices", "Civil Unrest", "Crop Yields", or "Drought" unless the user explicitly mentions them
3. If the user mentions "AI becomes president", create nodes like "AI Leadership", "Automated Governance", "Human-AI Interaction", NOT generic "Technology Policy" or "Society"
4. If the user mentions specific technologies, policies, events, or actors - use those EXACT concepts in your nodes
5. Each node MUST include a "stage" field matching one of the kill chain stages
6. Each edge MUST include "stage_transition" with Unicode arrow → (not ->)
7. stage_transition must connect consecutive kill chain stages (e.g., "Reconnaissance→Weaponization")
8. Generate 3-8 nodes and 2-6 edges that reflect the CAUSAL RELATIONSHIPS described in the prompt
9. Use node IDs with domain prefixes: ENV_ for Environment, ECO_ for Economy, SOC_ for Society, POL_ for Policy, TEC_ for Technology
10. Return ONLY valid JSON, no markdown code blocks, no explanatory text
11. Think creatively - each prompt should produce a UNIQUE network structure

Example (DO NOT reuse these nodes unless the user mentions them):
If prompt: "drought reduces crop yields and impacts food prices" → Create "Drought", "Crop Yields", "Food Prices"
If prompt: "AI becomes president" → Create "AI Leadership", "Automated Decision-Making", "Public Trust in AI", "Political Resistance"
If prompt: "trade war affects semiconductors" → Create "Trade Restrictions", "Semiconductor Supply", "Tech Manufacturing", "Global Supply Chains"

Remember: Generate NEW nodes for EACH unique prompt. Do not copy patterns from examples."""
    
    user_content = f"""User Scenario Prompt:
"{prompt}"

Stage Configurations:
{json.dumps(stage_configs, indent=2) if stage_configs else "{}"}

Task: Analyze the scenario prompt above and generate a DBN structure with nodes and edges that specifically reflect the entities, events, and causal relationships mentioned in that prompt. 

Be specific and context-aware - extract the actual concepts from the user's text rather than using generic examples.

Return the JSON structure now:"""
    
    # Prepare Groq API request (OpenAI-compatible format)
    headers = {
        "Authorization": f"Bearer {settings.LLAMA_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": settings.LLAMA_MODEL or "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.8,
        "top_p": 0.9,
        "max_tokens": 2000,
        "response_format": {"type": "json_object"}  # Request JSON response
    }
    
    # Log the request details
    logger.info(f"🟠 [GROQ] Sending prompt to Groq API")
    logger.info(f"🟠 [GROQ] URL: {settings.LLAMA_API_URL}")
    logger.info(f"🟠 [GROQ] Model: {payload['model']}")
    logger.info(f"🟠 [GROQ] User prompt: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                settings.LLAMA_API_URL,
                json=payload,
                headers=headers
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Log the raw response for debugging
            logger.info(f"🔴 [GROQ RESPONSE] Received response, status: {resp.status_code}")
            
            # Extract content from Groq response (OpenAI-compatible format)
            content = data["choices"][0]["message"]["content"]
            
            if not content:
                logger.error("❌ Empty response from Groq API")
                logger.debug(f"Full Groq response: {data}")
                return _get_mock_response()
            
            # Log raw response preview
            logger.info(f"🔴 [GROQ RESPONSE] Raw response preview (first 300 chars): {content[:300]}")
            logger.info(f"🔴 [GROQ RESPONSE] Response length: {len(content)} chars")
            
            # Try to extract JSON from the response
            llama_json = None
            try:
                # Try direct JSON parsing first
                llama_json = json.loads(content)
                logger.info(f"✅ [GROQ RESPONSE] Successfully parsed JSON from Groq response")
            except json.JSONDecodeError as e:
                logger.warning(f"Direct JSON parsing failed: {e}, trying regex extraction")
                # Fallback: Extract JSON using regex
                match = re.search(r"\{.*\}", content, re.DOTALL)
                if match:
                    try:
                        llama_json = json.loads(match.group(0))
                        logger.info(f"✅ [GROQ RESPONSE] Successfully extracted JSON using regex fallback")
                    except json.JSONDecodeError as e2:
                        logger.error(f"Regex extraction also failed: {e2}")
                        logger.debug(f"Extracted JSON string: {match.group(0)[:200] if match else 'N/A'}")
                else:
                    logger.warning("No JSON object found in Groq response")
                    logger.debug(f"Response content (first 500 chars): {content[:500]}")
            
            if not llama_json:
                logger.warning("No valid JSON returned; using fallback.")
                return _get_mock_response()
            
            # Log parsed node information
            logger.info(f"✅ [GROQ RESPONSE] Parsed nodes count: {len(llama_json.get('nodes', []))}")
            logger.info(f"✅ [GROQ RESPONSE] Parsed edges count: {len(llama_json.get('edges', []))}")
            node_labels = [n.get('label', 'N/A') for n in llama_json.get('nodes', [])[:5]]
            logger.info(f"✅ [GROQ RESPONSE] First 5 node labels: {node_labels}")
            
            # Return the parsed JSON directly (normalization happens in forecasts.py)
            return llama_json
            
    except httpx.TimeoutException:
        logger.warning(f"Groq API timeout at {settings.LLAMA_API_URL}, using mock response")
        return _get_mock_response()
    except httpx.HTTPStatusError as e:
        logger.warning(f"Groq API HTTP error {e.response.status_code}: {e.response.text}, using mock response")
        return _get_mock_response()
    except httpx.RequestError as e:
        logger.warning(f"Groq API request failed: {e}, using mock response")
        return _get_mock_response()
    except Exception as e:
        logger.warning(f"Groq API error: {e}, using mock response", exc_info=True)
        return _get_mock_response()

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
