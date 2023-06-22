from fastapi import APIRouter, Depends
from ..database import get_db
from . import file_models, schemas
from fastapi import File, UploadFile
from . import utils as file_utils
from ..core.oauth2 import require_user
from sqlalchemy.orm import Session

router = APIRouter()
# upload file
@router.post("/upload", response_model=schemas.FileResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db),user_id: str = Depends(require_user)):
    file_path = file_utils.save_file(file)
    db_file = file_models.File(filename=file.filename, content_type=file.content_type,file_path=file_path,created_by=user_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "content_type": db_file.content_type,
        "file_path":db_file.file_path,
        "created_by":db_file.created_by
    }