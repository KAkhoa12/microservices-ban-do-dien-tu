from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone_number: Optional[str] = None
    address: Optional[str] = None
    image: Optional[str] = None
    user_role: Optional[str] = "customer"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
class UserUpdateAvatar(BaseModel):
    user_id: int

class UserUpdate(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    user_role: Optional[str] = "customer"
    is_delete: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    full_name: Optional[str] = None
    is_delete: bool = False


class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
