from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException
from datetime import datetime

from models.order import Order, OrderDetail
from models.cart import CartDetail
from schemas.order import OrderCreate, OrderUpdate, OrderDetailCreate
from crud.product import get_product, update_product_stock
from core.response import Response, StatusEnum, CodeEnum

def get_orders_unified(
    skip: int = 0,
    take: int = 10,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    order_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = None
):
    """Unified function to get orders with pagination and filtering"""
    query = db.query(Order)
    
    # Apply filters
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    if order_id:
        query = query.filter(Order.id == order_id)
    
    if search:
        query = query.filter(Order.status.ilike(f"%{search}%"))
    
    # Order by created_at desc
    query = query.order_by(desc(Order.created_at))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    orders = query.offset(skip).limit(take).all()
    
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get orders successfully",
        data={
            "items": orders,
            "total": total,
            "skip": skip,
            "take": take
        }
    )

def get_order(order_id: int, db: Session):
    """Get single order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Order not found"
        )
    
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get order successfully",
        data=order
    )

def create_order(order: OrderCreate, db: Session):
    """Create new order"""
    try:
        # Create order
        db_order = Order(
            user_id=order.user_id,
            total_price=order.total_price,
            status=order.status,
            created_at=datetime.now()
        )
        db.add(db_order)
        db.flush()  # Get the order ID without committing
        
        # Create order details
        for detail in order.order_details:
            # Check product availability
            product = get_product(detail.product_id, db)
            if not product or product.status != StatusEnum.SUCCESS:
                db.rollback()
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.NOT_FOUND,
                    message=f"Product {detail.product_id} not found"
                )
            
            # Check stock
            if product.data.stock < detail.quantity:
                db.rollback()
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.BAD_REQUEST,
                    message=f"Insufficient stock for product {detail.product_id}"
                )
            
            # Create order detail
            db_order_detail = OrderDetail(
                order_id=db_order.id,
                product_id=detail.product_id,
                product_options=detail.product_options,
                quantity=detail.quantity,
                price=detail.price
            )
            db.add(db_order_detail)
            
            # Update product stock
            update_product_stock(detail.product_id, -detail.quantity, db)
        
        db.commit()
        db.refresh(db_order)
        
        return Response(
            status=StatusEnum.SUCCESS,
            code=CodeEnum.SUCCESS,
            message="Order created successfully",
            data=db_order
        )
        
    except Exception as e:
        db.rollback()
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.INTERNAL_SERVER_ERROR,
            message=f"Error creating order: {str(e)}"
        )

def create_order_from_cart(user_id: int, db: Session):
    """Create order from user's cart"""
    try:
        # Get cart items
        cart_items = db.query(CartDetail).filter(CartDetail.user_id == user_id).all()
        
        if not cart_items:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.BAD_REQUEST,
                message="Cart is empty"
            )
        
        # Calculate total and prepare order details
        total_price = 0.0
        order_details = []
        
        for cart_item in cart_items:
            product = get_product(cart_item.product_id, db)
            if not product or product.status != StatusEnum.SUCCESS:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.NOT_FOUND,
                    message=f"Product {cart_item.product_id} not found"
                )
            
            # Check stock
            if product.data.stock < cart_item.quantity:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.BAD_REQUEST,
                    message=f"Insufficient stock for product {cart_item.product_id}"
                )
            
            # Calculate price
            price = product.data.old_price if product.data.old_price else product.data.price
            item_total = price * cart_item.quantity
            total_price += item_total
            
            order_details.append(OrderDetailCreate(
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=price
            ))
        
        # Create order
        order_data = OrderCreate(
            user_id=user_id,
            total_price=total_price,
            order_details=order_details
        )
        
        result = create_order(order_data, db)
        
        if result.status == StatusEnum.SUCCESS:
            # Clear cart after successful order creation
            db.query(CartDetail).filter(CartDetail.user_id == user_id).delete()
            db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.INTERNAL_SERVER_ERROR,
            message=f"Error creating order from cart: {str(e)}"
        )

def update_order(order_id: int, order: OrderUpdate, db: Session):
    """Update order"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Order not found"
        )
    
    # Update fields
    if order.total_price is not None:
        db_order.total_price = order.total_price
    if order.status is not None:
        db_order.status = order.status
    
    db.commit()
    db.refresh(db_order)
    
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Order updated successfully",
        data=db_order
    )

def update_order_status(order_id: int, status: str, db: Session):
    """Update order status"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Order not found"
        )
    
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Order status updated successfully",
        data=db_order
    )

def cancel_order(order_id: int, db: Session):
    """Cancel order and restore stock"""
    try:
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.NOT_FOUND,
                message="Order not found"
            )
        
        if db_order.status in ["completed", "cancelled"]:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.BAD_REQUEST,
                message="Cannot cancel completed or already cancelled order"
            )
        
        # Restore stock for each order detail
        order_details = db.query(OrderDetail).filter(OrderDetail.order_id == order_id).all()
        for detail in order_details:
            update_product_stock(detail.product_id, detail.quantity, db)
        
        # Update order status
        db_order.status = "cancelled"
        db.commit()
        db.refresh(db_order)
        
        return Response(
            status=StatusEnum.SUCCESS,
            code=CodeEnum.SUCCESS,
            message="Order cancelled successfully",
            data=db_order
        )
        
    except Exception as e:
        db.rollback()
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.INTERNAL_SERVER_ERROR,
            message=f"Error cancelling order: {str(e)}"
        )

def delete_order(order_id: int, db: Session):
    """Delete order (admin only)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Order not found"
        )
    
    # Delete order details first (cascade should handle this, but being explicit)
    db.query(OrderDetail).filter(OrderDetail.order_id == order_id).delete()
    
    # Delete order
    db.delete(order)
    db.commit()
    
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Order deleted successfully"
    )
