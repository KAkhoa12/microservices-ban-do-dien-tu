from typing import Optional, List
from pydantic import BaseModel

class GiaiPhapAmThanh(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    content: str
    image_url: Optional[str] = None
    created_at: Optional[str]

class GiaiPhapAmThanhCreate(BaseModel):
    title: str
    description: str
    content: str

class GiaiPhapAmThanhUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None