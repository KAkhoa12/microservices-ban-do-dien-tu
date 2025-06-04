from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.cart import Cart, CartDetail, CartStatus
from schemas.cart import CartDetailCreate, CartDetailUpdate
from crud.product import get_product
from core.response import Response, StatusEnum, CodeEnum

# Cart CRUD operations
def get_or_create_cart(user_id: int, db: Session):
    """Get active cart for user or create new one"""
    cart = db.query(Cart).filter(
        Cart.user_id == user_id,
        Cart.status == CartStatus.ACTIVE
    ).first()

    if not cart:
        cart = Cart(user_id=user_id, status=CartStatus.ACTIVE)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart

def get_cart(user_id: int, db: Session):
    cart = get_or_create_cart(user_id, db)
    total_price = get_cart_total(cart.id, db)

    # Get cart details with product information
    cart_details = get_cart_details_with_products(cart.id, db)

    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get cart successfully",
        data={
            "cart": {
                "id": cart.id,
                "created_at": cart.created_at,
                "user_id": cart.user_id,
                "status": cart.status,
                "cart_details": cart_details
            },
            "total_price": total_price
        }
    )

def update_cart_status(cart_id: int, status: CartStatus, db: Session):
    """Update cart status"""
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Cart not found"
        )

    cart.status = status
    db.commit()
    db.refresh(cart)

    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Cart status updated successfully",
        data=cart
    )

def get_cart_item(cart_item_id: int, db: Session):
    cart_item = db.query(CartDetail).filter(CartDetail.id == cart_item_id).first()
    if not cart_item:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Cart item not found"
        )
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get cart item successfully",
        data=cart_item
    )

# CartDetail CRUD operations
def add_to_cart(user_id: int, cart_item: CartDetailCreate, db: Session):
    """Add item to cart"""
    # Get or create active cart
    cart = get_or_create_cart(user_id, db)

    # Check if product exists and has enough stock
    product = get_product(cart_item.product_id, db)
    if not product:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Product not found"
        )
    if product.data.stock < cart_item.quantity:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.BAD_REQUEST,
            message="Insufficient stock"
        )

    # Check if item already exists in cart
    existing_item = db.query(CartDetail).filter(
        CartDetail.cart_id == cart.id,
        CartDetail.product_id == cart_item.product_id
    ).first()

    if existing_item:
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return Response(
            status=StatusEnum.SUCCESS,
            code=CodeEnum.SUCCESS,
            message="Cart item updated successfully",
            data=existing_item
        )

    db_cart_item = CartDetail(
        cart_id=cart.id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity
    )
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Cart item added successfully",
        data=db_cart_item
    )

def update_cart_item(cart_item_id: int, cart_item: CartDetailUpdate, db: Session):
    db_cart_item = db.query(CartDetail).filter(CartDetail.id == cart_item_id).first()
    if not db_cart_item:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Cart item not found"
        )

    # Check if product has enough stock
    product = get_product(db_cart_item.product_id, db)
    if product.data.stock < cart_item.quantity:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.BAD_REQUEST,
            message="Insufficient stock"
        )

    db_cart_item.quantity = cart_item.quantity
    db.commit()
    db.refresh(db_cart_item)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Cart item updated successfully",
        data=db_cart_item
    )

def delete_cart_item(cart_item_id: int, db: Session):
    cart_item = db.query(CartDetail).filter(CartDetail.id == cart_item_id).first()
    if not cart_item:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Cart item not found"
        )
    db.delete(cart_item)
    db.commit()
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Cart item deleted successfully"
    )

def clear_cart(user_id: int, db: Session):
    """Clear all items from user's active cart"""
    cart = get_or_create_cart(user_id, db)
    db.query(CartDetail).filter(CartDetail.cart_id == cart.id).delete()
    db.commit()
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Cart cleared successfully"
    )

def remove_from_cart(user_id: int, product_id: int, db: Session):
    """Remove specific product from cart"""
    cart = get_or_create_cart(user_id, db)
    cart_item = db.query(CartDetail).filter(
        CartDetail.cart_id == cart.id,
        CartDetail.product_id == product_id
    ).first()

    if not cart_item:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Cart item not found"
        )

    db.delete(cart_item)
    db.commit()
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Cart item removed successfully"
    )

def update_cart_item_quantity(user_id: int, product_id: int, quantity: int, db: Session):
    """Update quantity of specific cart item"""
    cart = get_or_create_cart(user_id, db)
    cart_item = db.query(CartDetail).filter(
        CartDetail.cart_id == cart.id,
        CartDetail.product_id == product_id
    ).first()

    if not cart_item:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Cart item not found"
        )

    # Check if product has enough stock
    product = get_product(cart_item.product_id, db)
    if product.data.stock < quantity:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.BAD_REQUEST,
            message="Insufficient stock"
        )

    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Cart item updated successfully",
        data=cart_item
    )

def get_cart_details_with_products(cart_id: int, db: Session):
    """Get cart details with full product information"""
    cart_items = db.query(CartDetail).filter(CartDetail.cart_id == cart_id).all()
    cart_details = []

    for item in cart_items:
        product_response = get_product(item.product_id, db)
        if product_response and product_response.status == StatusEnum.SUCCESS:
            product_data = product_response.data
            cart_detail = {
                "id": item.id,
                "cart_id": item.cart_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product": {
                    "id": product_data.id,
                    "name": product_data.name,
                    "price": product_data.price,
                    "old_price": product_data.old_price,
                    "image_url": product_data.image_url,
                    "stock": product_data.stock,
                    "description": product_data.description,
                    "category_id": product_data.category_id,
                    "brand_id": product_data.brand_id
                }
            }
            cart_details.append(cart_detail)

    return cart_details

def get_cart_total(cart_id: int, db: Session) -> float:
    """Calculate total price for cart"""
    cart_items = db.query(CartDetail).filter(CartDetail.cart_id == cart_id).all()
    total = 0.0
    for item in cart_items:
        product = get_product(item.product_id, db)
        if product and product.status == StatusEnum.SUCCESS:
            price = product.data.old_price if product.data.old_price else product.data.price
            total += price * item.quantity
    return total
