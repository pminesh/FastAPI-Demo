from pydantic import BaseModel
import uuid

class FileCreate(BaseModel):
    filename: str
    content_type: str

class FileResponse(FileCreate):
    id: uuid.UUID
    file_path: str
    created_by: uuid.UUID