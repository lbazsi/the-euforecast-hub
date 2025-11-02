from fastapi import APIRouter, Depends, Query, Body
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging
from app.core.database import get_session
from app.models.forecast import Forecast
from app.schemas.common import SuccessResponse
from app.utils.responses import error_response
from app.services.llama_client import get_llama_forecast, normalize_llm_spec

logger = logging.getLogger(__name__)
router = APIRouter()

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
    """Generate a forecast using LLaMA and return DBN structure."""
    try:
        prompt = payload.get("prompt", "")
        stage_configs = payload.get("stage_configs", {})
        
        if not prompt:
            return error_response("BAD_REQUEST", "Prompt is required", 400)
        
        # Call LLaMA to get forecast structure
        raw_llama_json = await get_llama_forecast(prompt, stage_configs)
        
        # Normalize LLM response to DBN spec format
        llama_json = normalize_llm_spec(raw_llama_json)
        
        # Return the structured response
        return {
            "success": True,
            "data": {
                "nodes": llama_json.get("nodes", []),
                "edges": llama_json.get("edges", []),
                "stage": raw_llama_json.get("stage", "Reconnaissance"),
                "using_fallback": raw_llama_json.get("stage") is None or len(llama_json.get("nodes", [])) == 0
            }
        }
    except Exception as e:
        logger.error(f"Failed to generate forecast: {e}", exc_info=True)
        return error_response("GENERATION_ERROR", f"Failed to generate forecast: {str(e)}", 500)
