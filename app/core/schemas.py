from pydantic import BaseModel, EmailStr, constr
import uuid
import datetime
from typing import List

class RoleBase(BaseModel):
    role_name: str

class RoleCreate(RoleBase):
    pass

class Role(BaseModel):
    id: uuid.UUID
    role_name: str

    class Config:
        orm_mode = True

class RoleResponse(Role):
    id: uuid.UUID
    role_name: str

class ListRoleResponse(BaseModel):
    status: str
    results: int
    roles: List[RoleResponse]

class UpdateRoleSchema(BaseModel):
    role_name: str
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    name: str
    email: str
    
class UserCreate(UserBase):
    role_id: uuid.UUID
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    role:RoleResponse
    created_at: datetime.datetime
    updated_at: datetime.datetime

class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    role_id: uuid.UUID
    role: Role

    class Config:
        orm_mode = True