from typing import Optional, List
from pydantic import BaseModel

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    old_price: Optional[float] = None
    tags: Optional[str] = None
    number_of_sell: Optional[int] = None
    number_of_like: Optional[int] = None
    image_url: Optional[str] = None
    brand_id: int
    category_id: int
    stock: int
    created_at: Optional[str]

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    old_price: Optional[float] = None
    brand_id: int
    tags: Optional[str] = None
    number_of_sell: Optional[int] = None
    number_of_like: Optional[int] = None
    category_id: int
    stock: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tags: Optional[str] = None
    number_of_sell: Optional[int] = None
    number_of_like: Optional[int] = None
    old_price: Optional[float] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    stock: Optional[int] = None 