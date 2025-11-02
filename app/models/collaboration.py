from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, func
from app.core.database import Base
from datetime import datetime
import uuid

class Collaboration(Base):
    __tablename__ = "collaborations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    project_description: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    upload_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())