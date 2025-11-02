from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List

class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    totalPages: int

class SuccessResponse(BaseModel):
    success: bool = True
    data: Any

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] | None = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
