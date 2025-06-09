from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db.database import get_db
from crud.order import *
from schemas.order import OrderCreate, OrderUpdate

router = APIRouter()

class CreateOrderFromCartRequest(BaseModel):
    user_id: int
    cart_data: dict
    payment_id: int

@router.get("/orders")
def api_get_orders(
    page: int = 1,
    take: int = 10,
    skip: Optional[int] = None,  # Keep for backward compatibility
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    order_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get orders with pagination and filtering"""
    # Calculate skip from page if skip is not provided
    if skip is None:
        skip = (page - 1) * take
    return get_orders_unified(skip, take, user_id, status, order_id, search, db)

@router.get("/get-order")
def api_get_order(order_id: int, db: Session = Depends(get_db)):
    """Get single order by ID"""
    return get_order(order_id, db)

@router.post("/create-order")
def api_create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create new order"""
    return create_order(order, db)

@router.post("/create-order-from-cart")
def api_create_order_from_cart(request: CreateOrderFromCartRequest, db: Session = Depends(get_db)):
    """Create order from cart data (for payment service)"""
    return create_order_from_cart_data(request.user_id, request.cart_data, request.payment_id, db)

@router.post("/create-order-from-user-cart")
def api_create_order_from_user_cart(user_id: int, db: Session = Depends(get_db)):
    """Create order from user's active cart"""
    return create_order_from_cart(user_id, db)

@router.put("/update-order")
def api_update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db)
):
    """Update order"""
    return update_order(order_id, order, db)

@router.put("/update-order-status")
def api_update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update order status"""
    return update_order_status(order_id, status, db)

@router.put("/cancel-order")
def api_cancel_order(order_id: int, db: Session = Depends(get_db)):
    """Cancel order and restore stock"""
    return cancel_order(order_id, db)

@router.delete("/delete-order")
def api_delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete order (admin only)"""
    return delete_order(order_id, db)
