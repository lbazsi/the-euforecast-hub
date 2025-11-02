import httpx
from app.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

async def get_llama_forecast(prompt: str, stage_configs: dict) -> dict:
    """Call Groq API (OpenAI-compatible) for forecast generation."""
    payload = {"message": prompt, "stageConfigurations": stage_configs}
    
    # Skip API call if URL is the default mock endpoint
    if settings.LLAMA_API_URL == "http://localhost:8000/mock-llama":
        logger.info("Using mock LLAMA response (default endpoint)")
        return _get_mock_response()
    
    # Check if using Groq API
    is_groq = "api.groq.com" in settings.LLAMA_API_URL
    
    if is_groq:
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set, using mock response")
            return _get_mock_response()
        
        # Format request for Groq (OpenAI-compatible)
        system_prompt = """You are a forecasting model generator that creates Dynamic Bayesian Network (DBN) structures.
Generate a JSON response with nodes and edges representing forecast scenarios.

Required format:
{
  "stage": "string (one of the kill chain stages)",
  "nodes": [
    {
      "id": "string (unique identifier like ECO_01, SOC_02)",
      "label": "string (human-readable name)",
      "impact": 0.0-1.0,
      "confidence": 0.0-1.0,
      "domain": "string (Economy, Society, Environment, Policy, Technology)"
    }
  ],
  "edges": [
    {
      "source": "node_id",
      "target": "node_id",
      "sign": "+" or "-",
      "strength": 0.0-1.0
    }
  ]
}

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
    else:
        # Original custom endpoint logic
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

def _get_mock_response() -> dict:
    """Deterministic mock response for development/testing."""
    return {
        "stage": "Exploitation",
        "nodes": [
            {"id":"ECO_04","label":"Food Prices Rise","impact":0.23,"confidence":0.74,"domain":"Economy"},
            {"id":"SOC_02","label":"Civil Unrest Increases","impact":0.15,"confidence":0.68,"domain":"Society"}
        ],
        "edges": [
            {"source":"ECO_04","target":"SOC_02","sign":"+","strength":0.6}
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
