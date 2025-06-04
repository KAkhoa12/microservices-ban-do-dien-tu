from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class OrderDetailBase(BaseModel):
    product_id: int
    product_options: Optional[str] = None
    quantity: int
    price: float

class OrderDetailCreate(OrderDetailBase):
    pass

class OrderDetailUpdate(BaseModel):
    product_options: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None

class OrderDetail(OrderDetailBase):
    id: Optional[int] = None
    order_id: Optional[int] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int
    total_price: float
    status: Optional[str] = "pending"

class OrderCreate(OrderBase):
    order_details: List[OrderDetailCreate] = []

class OrderUpdate(BaseModel):
    total_price: Optional[float] = None
    status: Optional[str] = None

class Order(OrderBase):
    id: Optional[int] = None
    created_at: Optional[str] = None
    order_details: List[OrderDetail] = []

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: str
    order_details: List[OrderDetail] = []

    class Config:
        from_attributes = True
