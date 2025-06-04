from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class CartStatus(str, Enum):
    ACTIVE = "active"
    ARRIVED = "arrived"
    COMPLETE = "complete"
    ERROR = "error"


class CartDetailBase(BaseModel):
    product_id: int
    quantity: int


class CartDetailCreate(CartDetailBase):
    product_id: int
    quantity: int


class CartDetailUpdate(BaseModel):
    quantity: int


class CartDetail(CartDetailBase):
    id: int
    cart_id: int

    class Config:
        from_attributes = True


class CartBase(BaseModel):
    user_id: int
    status: CartStatus = CartStatus.ACTIVE


class CartCreate(CartBase):
    pass


class CartUpdate(BaseModel):
    status: CartStatus


class Cart(CartBase):
    id: int
    created_at: str
    cart_details: List[CartDetail] = []

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    cart: Cart
    total_price: float