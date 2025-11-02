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
    """Call LLM API (Groq, Ollama, or custom) for forecast generation."""
    
    # Skip API call if URL is the default mock endpoint
    if settings.LLAMA_API_URL == "http://localhost:8000/mock-llama":
        logger.info("Using mock LLAMA response (default endpoint)")
        return _get_mock_response()
    
    # Check API type
    is_groq = "api.groq.com" in settings.LLAMA_API_URL
    is_ollama = "/api/generate" in settings.LLAMA_API_URL or "11434" in settings.LLAMA_API_URL
    
    if is_groq:
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set, using mock response")
            return _get_mock_response()
        
        # Format request for Groq (OpenAI-compatible)
        system_prompt = """You are a forecasting model generator that creates Dynamic Bayesian Network (DBN) structures.
Generate a JSON response with nodes and edges representing forecast scenarios.

Kill chain stages (in order):
["Reconnaissance","Weaponization","Delivery","Exploitation","Installation","Command & Control (C2)","Actions on Objectives"]

Required format:
{
  "stage": "string (one of the kill chain stages)",
  "nodes": [
    {
      "id": "string (unique identifier like ECO_01, SOC_02)",
      "label": "string (human-readable name)",
      "domain": "string (Economy, Society, Environment, Policy, Technology)",
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

Rules:
- Each node MUST include "stage" field.
- Each edge MUST include "stage_transition" with Unicode arrow → (not ->).
- stage_transition must connect consecutive kill chain stages (e.g., "Reconnaissance→Weaponization").

Based on the stage configurations and prompt, generate appropriate nodes and edges."""
        
        user_content = f"""Prompt: {prompt}

Stage Configurations:
{json.dumps(stage_configs, indent=2)}

Generate a DBN graph structure in the required JSON format."""
        
        groq_payload = {
            "model": "llama-3.1-70b-versatile",  # or "mixtral-8x7b-32768"
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"}  # Request JSON response
        }
        
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    settings.LLAMA_API_URL,
                    json=groq_payload,
                    headers=headers
                )
                resp.raise_for_status()
                data = resp.json()
                
                # Extract content from Groq response
                content = data["choices"][0]["message"]["content"]
                
                # Parse JSON from response
                try:
                    llama_json = json.loads(content)
                    logger.info("Successfully received response from Groq API")
                    return llama_json
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from Groq response: {e}")
                    logger.debug(f"Response content: {content}")
                    return _get_mock_response()
                    
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
            logger.warning(f"Groq API error: {e}, using mock response")
            return _get_mock_response()
    elif is_ollama:
        # Ollama API format
        if not settings.LLAMA_MODEL:
            logger.warning("LLAMA_MODEL not set for Ollama, using mock response")
            return _get_mock_response()
        
        # Build system prompt and user content
        system_prompt = """You are a forecasting model generator that creates Dynamic Bayesian Network (DBN) structures.
Generate a JSON response with nodes and edges representing forecast scenarios.

Kill chain stages (in order):
["Reconnaissance","Weaponization","Delivery","Exploitation","Installation","Command & Control (C2)","Actions on Objectives"]

Required format:
{
  "stage": "string (one of the kill chain stages)",
  "nodes": [
    {
      "id": "string (unique identifier like ECO_01, SOC_02)",
      "label": "string (human-readable name)",
      "domain": "string (Economy, Society, Environment, Policy, Technology)",
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

Rules:
- Each node MUST include "stage" field.
- Each edge MUST include "stage_transition" with Unicode arrow → (not ->).
- stage_transition must connect consecutive kill chain stages (e.g., "Reconnaissance→Weaponization").
- Return ONLY valid JSON, no markdown formatting."""
        
        user_content = f"""Prompt: {prompt}

Stage Configurations:
{json.dumps(stage_configs, indent=2)}

Generate a DBN graph structure in the required JSON format. Return only the JSON object, no additional text."""
        
        # Combine into a single prompt for Ollama
        full_prompt = f"{system_prompt}\n\n{user_content}"
        
        ollama_payload = {
            "model": settings.LLAMA_MODEL or "llama3",
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": 0.7},
            "format": "json"  # Request JSON response format
        }
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    settings.LLAMA_API_URL,
                    json=ollama_payload
                )
                resp.raise_for_status()
                data = resp.json()
                
                # Extract response from Ollama format
                content = data.get("response", "")
                if not content:
                    logger.error("Empty response from Ollama API")
                    logger.debug(f"Full Ollama response: {data}")
                    return _get_mock_response()
                
                # Parse JSON from response with robust extraction
                content = content.strip()
                
                # Remove markdown code blocks if present
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                # Try direct JSON parsing first
                llama_json = None
                try:
                    llama_json = json.loads(content)
                    logger.info("Successfully parsed JSON from Ollama response")
                    return llama_json
                except json.JSONDecodeError as e:
                    logger.warning(f"Direct JSON parsing failed: {e}, trying regex extraction")
                    
                # Fallback: Extract JSON using regex (look for { ... } pattern)
                if llama_json is None:
                    try:
                        # Match JSON object with balanced braces
                        match = re.search(r"\{.*\}", content, re.DOTALL)
                        if match:
                            json_str = match.group(0)
                            llama_json = json.loads(json_str)
                            logger.info("Successfully extracted JSON using regex fallback")
                            return llama_json
                        else:
                            logger.warning("No JSON object found in Ollama response")
                            logger.debug(f"Response content (first 500 chars): {content[:500]}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Regex extraction also failed: {e}")
                        logger.debug(f"Extracted JSON string: {match.group(0)[:200] if match else 'N/A'}")
                
                # If all parsing attempts fail, log and return mock
                logger.error(f"Failed to parse JSON from Ollama response after all attempts")
                logger.debug(f"Full response content: {content}")
                return _get_mock_response()
                    
        except httpx.TimeoutException:
            logger.warning(f"Ollama API timeout at {settings.LLAMA_API_URL}, using mock response")
            return _get_mock_response()
        except httpx.HTTPStatusError as e:
            logger.warning(f"Ollama API HTTP error {e.response.status_code}: {e.response.text}, using mock response")
            return _get_mock_response()
        except httpx.RequestError as e:
            logger.warning(f"Ollama API request failed: {e}, using mock response")
            return _get_mock_response()
        except Exception as e:
            logger.warning(f"Ollama API error: {e}, using mock response")
            return _get_mock_response()
    else:
        # Original custom endpoint logic
        payload = {"message": prompt, "stageConfigurations": stage_configs}
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(settings.LLAMA_API_URL, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data
        except httpx.TimeoutException:
            logger.warning(f"LLAMA API timeout at {settings.LLAMA_API_URL}, using mock response")
            return _get_mock_response()
        except httpx.RequestError as e:
            logger.warning(f"LLAMA API request failed: {e}, using mock response")
            return _get_mock_response()
        except Exception as e:
            logger.warning(f"LLAMA API error: {e}, using mock response")
            return _get_mock_response()

def normalize_llm_spec(raw: dict) -> dict:
    """
    Convert LLM output into the DBN engine's expected shape:
    - edges[].stage_transition (Unicode arrow)
    - edges[].strength_hint, edges[].llm_confidence
    - nodes[].stage
    """
    out = {"nodes": [], "edges": []}
    nodes = raw.get("nodes", [])
    edges = raw.get("edges", [])

    # Normalize nodes
    for n in nodes:
        node_id = n.get("id") or n.get("label", "NODE").upper().replace(" ", "_")
        out["nodes"].append({
            "id": node_id,
            "label": n.get("label", "Unknown"),
            "domain": n.get("domain", "Environment"),
            "stage": n.get("stage") or "Reconnaissance",  # default; backfilled below from edges
            "state_type": "discrete",
            "state_space": ["low", "med", "high"],
        })

    # Index
    node_by_id = {n["id"]: n for n in out["nodes"]}

    # Normalize edges
    for e in edges:
        st = e.get("stage_transition", "")
        st = st.replace("->", "→") if st else ""  # ASCII to Unicode

        edge = {
            "source": e.get("source"),
            "target": e.get("target"),
            "stage_transition": st or "",  # may fill below
            "strength_hint": float(e.get("strength_hint", e.get("strength", 0.6))),
            "llm_confidence": float(e.get("llm_confidence", e.get("confidence", 0.7))),
        }
        out["edges"].append(edge)

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
