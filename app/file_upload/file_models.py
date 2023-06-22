from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, text, Boolean
from ..database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class File(Base):
    __tablename__ = "files_tb"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    filename = Column(String)
    file_path = Column(String)
    content_type = Column(String)
    created_by = Column(UUID(as_uuid=True))