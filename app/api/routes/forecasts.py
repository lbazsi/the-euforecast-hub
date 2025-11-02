from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_session
from app.models.forecast import Forecast
from app.schemas.common import SuccessResponse
from app.utils.responses import error_response

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
