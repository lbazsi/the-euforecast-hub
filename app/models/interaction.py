from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, func, Float, Boolean
from app.core.database import Base, JSONType
from datetime import datetime
import uuid

class LLMInteraction(Base):
    """Store LLM interactions for continuous learning and analysis."""
    __tablename__ = "llm_interactions"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    stage_configs: Mapped[dict] = mapped_column(JSONType, default=dict)
    llama_output: Mapped[dict] = mapped_column(JSONType, default=dict)
    normalized_spec: Mapped[dict] = mapped_column(JSONType, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Optional metadata
    user_id: Mapped[str | None] = mapped_column(String, nullable=True)
    session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str | None] = mapped_column(String(32), nullable=True)  # e.g., "forecasts/generate", "builder/run"
    
    # Performance metrics
    response_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)  # e.g., "llama3", "llama-3.1-70b"
    
    # Quality indicators
    using_fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

