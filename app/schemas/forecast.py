from pydantic import BaseModel, Field, constr, field_validator
from typing import Optional, Dict, Any

class ForecastCreate(BaseModel):
    name: constr(min_length=3, max_length=200)
    publisherName: constr(min_length=2, max_length=100)
    projectKeywords: constr(min_length=1, max_length=500)
    projectDescription: constr(min_length=10, max_length=5000)
    metadata: Optional[Dict[str, Any]] = {}

class ForecastItem(BaseModel):
    id: str
    name: str
    publisherName: str
    projectKeywords: str
    projectDescription: str
    status: str
    category: str
    createdAt: str
    updatedAt: str

class ForecastDetail(BaseModel):
    id: str
    name: str
    publisherName: str
    projectKeywords: str
    projectDescription: str
    status: str
    category: str
    metadata: Dict[str, Any]
    createdAt: str
    updatedAt: str
