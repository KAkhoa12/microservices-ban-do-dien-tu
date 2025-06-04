from typing import Optional, List
from pydantic import BaseModel

class CongTrinhToanDien(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    content: str
    image_url: Optional[str] = None
    created_at: Optional[str]

class CongTrinhToanDienCreate(BaseModel):
    title: str
    description: str
    content: str

class CongTrinhToanDienUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None