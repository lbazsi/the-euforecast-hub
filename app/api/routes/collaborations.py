from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_session
from app.models.collaboration import Collaboration
from app.schemas.collaboration import CollaborationCreate
from app.utils.responses import error_response

router = APIRouter()

@router.get("/collaborations")
async def list_collaborations(
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    session: AsyncSession = Depends(get_session)
):
    stmt = select(Collaboration)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            (Collaboration.name.ilike(like)) |
            (Collaboration.email.ilike(like)) |
            (Collaboration.project_description.ilike(like))
        )
    total = (await session.execute(stmt.with_only_columns(func.count()))).scalar_one()
    stmt = stmt.order_by(Collaboration.created_at.desc()).offset((page-1)*limit).limit(limit)
    rows = (await session.execute(stmt)).scalars().all()
    items = [{
        "id": r.id,
        "name": r.name,
        "email": r.email,
        "projectDescription": r.project_description,
        "uploadedFileName": r.uploaded_file_name,
        "uploadType": r.upload_type,
        "status": r.status,
        "createdAt": r.created_at.isoformat()
    } for r in rows]
    return {"success": True, "data": {"collaborations": items, "pagination": {
        "page": page, "limit": limit, "total": total, "totalPages": (total + limit - 1)//limit
    }}}

@router.get("/collaborations/{id}")
async def get_collaboration(id: str, session: AsyncSession = Depends(get_session)):
    r = await session.get(Collaboration, id)
    if not r:
        error_response("NOT_FOUND", "Collaboration not found", 404)
    return {"success": True, "data": {
        "id": r.id,
        "name": r.name,
        "email": r.email,
        "projectDescription": r.project_description,
        "uploadedFileName": r.uploaded_file_name,
        "uploadType": r.upload_type,
        "status": r.status,
        "createdAt": r.created_at.isoformat()
    }}

@router.post("/collaborations", status_code=201)
async def create_collaboration(payload: CollaborationCreate, session: AsyncSession = Depends(get_session)):
    rec = Collaboration(
        name=payload.name,
        email=payload.email,
        project_description=payload.projectDescription,
        uploaded_file_name=payload.uploadedFileName,
        upload_type=payload.uploadType
    )
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    return {"success": True, "data": {"id": rec.id, "message": "Collaboration opportunity submitted successfully"}}

@router.post("/collaborations/{id}/contact")
async def contact_collaborator(
    id: str,
    requesterName: str,
    requesterEmail: str,
    message: str,
    session: AsyncSession = Depends(get_session)
):
    r = await session.get(Collaboration, id)
    if not r:
        error_response("NOT_FOUND", "Collaboration not found", 404)
    # MVP: no email sending; just acknowledge
    return {"success": True, "data": {"message": "Contact request sent successfully"}}
