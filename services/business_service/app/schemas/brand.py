from typing import Optional
from pydantic import BaseModel

class Brand(BaseModel):
    id: Optional[int] = None
    name: str = None
    image_url: str = None
    slug: str = None
    created_at: Optional[str] 

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    
class BrandCreate(BaseModel):
    name: str
    slug: str