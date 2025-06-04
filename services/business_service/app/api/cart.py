from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from crud.cart import *
from schemas.cart import CartDetailCreate, CartDetailUpdate, CartStatus
from models.cart import CartStatus

router = APIRouter()

@router.get("/get-cart")
def api_get_cart(user_id: int, db: Session = Depends(get_db)):
    """Get user's cart with all items and total price"""
    return get_cart(user_id, db)

@router.post("/add-to-cart")
def api_add_to_cart(user_id: int, cart_item: CartDetailCreate, db: Session = Depends(get_db)):
    """Add item to cart"""
    return add_to_cart(user_id, cart_item, db)

@router.put("/update-cart-item")
def api_update_cart_item(
    user_id: int,
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    return update_cart_item_quantity(user_id, product_id, quantity, db)

@router.delete("/remove-from-cart")
def api_remove_from_cart(user_id: int, product_id: int, db: Session = Depends(get_db)):
    """Remove item from cart"""
    return remove_from_cart(user_id, product_id, db)

@router.delete("/clear-cart")
def api_clear_cart(user_id: int, db: Session = Depends(get_db)):
    """Clear all items from cart"""
    return clear_cart(user_id, db)

@router.put("/update-cart-status")
def api_update_cart_status(cart_id: int, status: CartStatus, db: Session = Depends(get_db)):
    """Update cart status"""
    return update_cart_status(cart_id, status, db)
