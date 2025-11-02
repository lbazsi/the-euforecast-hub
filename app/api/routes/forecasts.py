from fastapi import APIRouter, Depends, Query, Body
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging
import time
import json
import hashlib
from pathlib import Path
from app.core.database import get_session
from app.models.forecast import Forecast
from app.models.interaction import LLMInteraction
from app.schemas.common import SuccessResponse
from app.utils.responses import error_response
from app.services.llama_client import get_llama_forecast, normalize_llm_spec
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Directory for storing forecast entries for DBN training
FORECAST_STORAGE_DIR = Path("data/forecasts")
FORECAST_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def store_forecast_entry(prompt: str, output: dict, normalized_spec: dict):
    """Store forecast entry for future DBN retraining."""
    try:
        # Create a hash-based filename from prompt
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        timestamp = int(time.time())
        filename = f"{timestamp}_{prompt_hash}.json"
        filepath = FORECAST_STORAGE_DIR / filename
        
        entry = {
            "prompt": prompt,
            "output": output,
            "normalized_spec": normalized_spec,
            "timestamp": timestamp,
        }
        
        with open(filepath, "w") as f:
            json.dump(entry, f, indent=2)
        
        logger.info(f"Stored forecast entry: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.warning(f"Failed to store forecast entry: {e}")
        return None

@router.get("/forecasts")
async def list_forecasts(
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    sortBy: str = "createdAt",
    order: str = "desc",
    session: AsyncSession = Depends(get_session)
):
    sort_map = {
        "createdAt": Forecast.created_at,
        "name": Forecast.name,
        "publisher": Forecast.publisher_name
    }
    sort_col = sort_map.get(sortBy, Forecast.created_at)
    sort_col = sort_col.desc() if order == "desc" else sort_col.asc()

    stmt = select(Forecast)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            (Forecast.name.ilike(like)) |
            (Forecast.publisher_name.ilike(like)) |
            (Forecast.project_keywords.ilike(like)) |
            (Forecast.project_description.ilike(like))
        )

    total = (await session.execute(stmt.with_only_columns(func.count()))).scalar_one()
    stmt = stmt.order_by(sort_col).offset((page-1)*limit).limit(limit)
    rows = (await session.execute(stmt)).scalars().all()
    items = [{
        "id": r.id,
        "name": r.name,
        "publisherName": r.publisher_name,
        "projectKeywords": r.project_keywords,
        "projectDescription": r.project_description,
        "status": r.status,
        "category": r.category,
        "createdAt": r.created_at.isoformat(),
        "updatedAt": r.updated_at.isoformat() if r.updated_at else r.created_at.isoformat()
    } for r in rows]

    return {"success": True, "data": {"forecasts": items, "pagination": {
        "page": page, "limit": limit, "total": total, "totalPages": (total + limit - 1)//limit
    }}}

@router.get("/forecasts/{id}")
async def get_forecast(id: str, session: AsyncSession = Depends(get_session)):
    r = await session.get(Forecast, id)
    if not r:
        return error_response("NOT_FOUND", "Forecast not found", 404)
    return {"success": True, "data": {
        "id": r.id,
        "name": r.name,
        "publisherName": r.publisher_name,
        "projectKeywords": r.project_keywords,
        "projectDescription": r.project_description,
        "status": r.status,
        "category": r.category,
        "metadata": r.meta_data,
        "createdAt": r.created_at.isoformat(),
        "updatedAt": r.updated_at.isoformat() if r.updated_at else r.created_at.isoformat()
    }}

from app.schemas.forecast import ForecastCreate

@router.post("/forecasts", status_code=201)
async def create_forecast(payload: ForecastCreate, session: AsyncSession = Depends(get_session)):
    rec = Forecast(
        name=payload.name,
        publisher_name=payload.publisherName,
        project_keywords=payload.projectKeywords,
        project_description=payload.projectDescription,
        meta_data=payload.metadata or {}
    )
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    return {"success": True, "data": {"id": rec.id, "message": "Forecast published successfully"}}

@router.post("/forecasts/generate")
async def generate_forecast(
    payload: Dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_session)
):
    """Generate a forecast using LLaMA and return DBN structure.
    
    Also stores the interaction for continuous learning and analysis.
    """
    start_time = time.time()
    prompt = payload.get("prompt", "")
    stage_configs = payload.get("stage_configs", {})
    user_id = payload.get("user_id")
    session_id = payload.get("session_id")
    
    if not prompt:
        return error_response("BAD_REQUEST", "Prompt is required", 400)
    
    raw_llama_json = None
    llama_json = None
    using_fallback = False
    error_msg = None
    
    try:
        # Call LLaMA to get forecast structure
        raw_llama_json = await get_llama_forecast(prompt, stage_configs)
        
        # Normalize LLM response to DBN spec format
        llama_json = normalize_llm_spec(raw_llama_json)
        
        # Check if fallback was used
        using_fallback = (
            raw_llama_json.get("stage") is None or 
            len(llama_json.get("nodes", [])) == 0 or
            settings.LLAMA_API_URL == "http://localhost:8000/mock-llama"
        )
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        
        # Store interaction for continuous learning (database)
        interaction = LLMInteraction(
            prompt=prompt,
            stage_configs=stage_configs,
            llama_output=raw_llama_json,
            normalized_spec=llama_json,
            user_id=user_id,
            session_id=session_id,
            source="forecasts/generate",
            response_time_ms=response_time_ms,
            model_version=settings.LLAMA_MODEL or "llama3",
            using_fallback=using_fallback
        )
        session.add(interaction)
        await session.commit()
        
        # Store forecast entry for DBN retraining (file system)
        if not using_fallback:  # Only store successful non-fallback forecasts
            store_forecast_entry(prompt, raw_llama_json, llama_json)
        
        # Return the structured response
        return {
            "success": True,
            "data": {
                "nodes": llama_json.get("nodes", []),
                "edges": llama_json.get("edges", []),
                "stage": raw_llama_json.get("stage", "Reconnaissance"),
                "using_fallback": using_fallback
            }
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to generate forecast: {e}", exc_info=True)
        
        # Store failed interaction for analysis
        try:
            response_time_ms = (time.time() - start_time) * 1000
            interaction = LLMInteraction(
                prompt=prompt,
                stage_configs=stage_configs,
                llama_output=raw_llama_json or {},
                normalized_spec=llama_json,
                user_id=user_id,
                session_id=session_id,
                source="forecasts/generate",
                response_time_ms=response_time_ms,
                model_version=settings.LLAMA_MODEL or "llama3",
                using_fallback=True,
                error_message=error_msg
            )
            session.add(interaction)
            await session.commit()
        except Exception as store_error:
            logger.warning(f"Failed to store interaction: {store_error}")
        
        return error_response("GENERATION_ERROR", f"Failed to generate forecast: {error_msg}", 500)
