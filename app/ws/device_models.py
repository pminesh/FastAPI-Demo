from sqlalchemy import Column, String, Boolean, Integer
from ..database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Device(Base):
    __tablename__ = "devices_tb"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    name = Column(String)
    device_type = Column(String)
    app_type = Column(String)
    device_id = Column(Integer)
    channel_id = Column(Integer)
    is_dimmable = Column(Boolean)
    status = Column(Boolean)