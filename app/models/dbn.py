from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base
import uuid

class DBNModelSpec(Base):
    __tablename__ = "dbn_specs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    spec: Mapped[dict] = mapped_column(JSONB, default=dict)  # validated LLM JSON
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped = mapped_column(DateTime(timezone=True), server_default=func.now())

class DBNModelVersion(Base):
    __tablename__ = "dbn_versions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    spec_id: Mapped[str] = mapped_column(String, nullable=False)
    params: Mapped[dict] = mapped_column(JSONB, default=dict)  # learned CPDs
    metrics: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped = mapped_column(DateTime(timezone=True), server_default=func.now())

class ForecastRun(Base):
    __tablename__ = "forecast_runs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_version_id: Mapped[str] = mapped_column(String, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSONB, default=dict)
    results: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped = mapped_column(DateTime(timezone=True), server_default=func.now())
