from typing import Optional, List
from pydantic import BaseModel

class Category(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    slug: str
    parent_id: Optional[int] = None
    created_at: Optional[str]

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str
    parent_id: Optional[int] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None 