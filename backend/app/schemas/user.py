from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int; email: str; name: Optional[str] = None
    phone: Optional[str] = None; is_active: bool; created_at: datetime
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str; token_type: str = "bearer"; user: UserResponse
