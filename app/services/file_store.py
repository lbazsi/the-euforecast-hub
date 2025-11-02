from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.upload import UploadFileBlob

async def save_file(session: AsyncSession, filename: str, content_type: str, data: bytes) -> UploadFileBlob:
    f = UploadFileBlob(filename=filename, content_type=content_type, size=len(data), data=data)
    session.add(f)
    await session.commit()
    await session.refresh(f)
    return f

async def get_file_by_name(session: AsyncSession, filename: str) -> UploadFileBlob | None:
    q = await session.execute(select(UploadFileBlob).where(UploadFileBlob.filename == filename))
    return q.scalars().first()
