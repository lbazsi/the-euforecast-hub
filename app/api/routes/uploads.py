from fastapi import APIRouter, UploadFile, File, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.file_store import save_file, get_file_by_name
from app.schemas.upload import UploadResponse
from app.utils.responses import error_response

router = APIRouter()

ALLOWED_TYPES = {"application/pdf","image/png","image/jpeg","image/svg+xml"}

@router.post("/uploads")
async def upload_file(file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        error_response("FILE_TOO_LARGE", "Max 10MB", 422)
    if file.content_type not in ALLOWED_TYPES:
        error_response("UNSUPPORTED_TYPE", "Only PDF/PNG/JPG/SVG", 422)

    rec = await save_file(session, file.filename, file.content_type, data)
    return {"success": True, "data": {
        "url": f"/api/v1/uploads/{rec.filename}",
        "fileName": rec.filename,
        "fileType": rec.content_type,
        "fileSize": rec.size
    }}

@router.get("/uploads/{filename}")
async def get_upload(filename: str, session: AsyncSession = Depends(get_session)):
    rec = await get_file_by_name(session, filename)
    if not rec:
        error_response("NOT_FOUND", "File not found", 404)
    return Response(content=rec.data, media_type=rec.content_type)
