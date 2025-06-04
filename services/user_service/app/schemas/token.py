from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str

class VerifyTokenRequest(BaseModel):
    access_token: str
    refresh_token: str 