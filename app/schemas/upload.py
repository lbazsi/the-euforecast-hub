from pydantic import BaseModel

class UploadResponse(BaseModel):
    url: str
    fileName: str
    fileType: str
    fileSize: int
