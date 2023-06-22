import uuid
from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base

class Role(Base):
    """Model representing a role in the database."""
    __tablename__ = 'roles_tb'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    role_name = Column(String, nullable=False)

    # Relationship with the User model
    users = relationship('User', back_populates='role')

class User(Base):
    """Model representing a user in the database."""
    __tablename__ = "users_tb"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    name = Column(String,  nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    verified = Column(Boolean, nullable=False, server_default='False')
    verification_code = Column(String, nullable=True, unique=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles_tb.id"))
    role = relationship('Role',back_populates="users")
