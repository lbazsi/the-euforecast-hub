from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class CollaborationCreate(BaseModel):
    name: constr(min_length=2, max_length=100)
    email: EmailStr
    projectDescription: constr(min_length=10, max_length=5000)
    uploadedFileName: Optional[str] = None
    uploadType: Optional[str] = None

class CollaborationItem(BaseModel):
    id: str
    name: str
    email: str
    projectDescription: str
    uploadedFileName: str | None
    uploadType: str | None
    status: str
    createdAt: str

class CollaborationDetail(CollaborationItem):
    pass
