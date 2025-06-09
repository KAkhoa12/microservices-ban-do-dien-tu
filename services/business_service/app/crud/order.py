from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from fastapi import HTTPException
from datetime import datetime

from models.order import Order, OrderDetail
from models.cart import CartDetail, Cart
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
    query = db.query(Order).options(joinedload(Order.order_details).joinedload(OrderDetail.product))

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

    # Transform orders to include product details
    orders_data = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "user_id": order.user_id,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "order_details": []
        }

        for detail in order.order_details:
            detail_dict = {
                "id": detail.id,
                "product_id": detail.product_id,
                "quantity": detail.quantity,
                "price": detail.price,
                "product_options": detail.product_options,
                "product": {
                    "id": detail.product.id,
                    "name": detail.product.name,
                    "price": detail.product.price,
                    "old_price": detail.product.old_price,
                    "image_url": detail.product.image_url,
                    "description": detail.product.description
                } if detail.product else None
            }
            order_dict["order_details"].append(detail_dict)

        orders_data.append(order_dict)

    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get orders successfully",
        data={
            "items": orders_data,
            "total": total,
            "skip": skip,
            "take": take
        }
    )

def get_order(order_id: int, db: Session):
    """Get single order by ID with detailed product information"""
    order = db.query(Order).options(
        joinedload(Order.order_details).joinedload(OrderDetail.product)
    ).filter(Order.id == order_id).first()

    if not order:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Order not found"
        )

    # Transform order to include product details
    order_dict = {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "order_details": []
    }

    for detail in order.order_details:
        detail_dict = {
            "id": detail.id,
            "product_id": detail.product_id,
            "quantity": detail.quantity,
            "price": detail.price,
            "product_options": detail.product_options,
            "product": {
                "id": detail.product.id,
                "name": detail.product.name,
                "price": detail.product.price,
                "old_price": detail.product.old_price,
                "image_url": detail.product.image_url,
                "description": detail.product.description
            } if detail.product else None
        }
        order_dict["order_details"].append(detail_dict)

    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get order successfully",
        data=order_dict
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
        print(f"Error creating order: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.SERVER_ERROR,
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
                price=price,
                product_options=""  # Provide empty string instead of None
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
            code=CodeEnum.SERVER_ERROR,
            message=f"Error creating order from cart: {str(e)}"
        )

def create_order_from_cart_data(user_id: int, cart_data: dict, payment_id: int, db: Session):
    """Create order from cart data (for payment service)"""
    try:
        # Parse cart data - handle both direct cart_details and nested cart structure
        cart_details = cart_data.get('cart_details', [])
        if not cart_details and 'cart' in cart_data:
            cart_details = cart_data.get('cart', {}).get('cart_details', [])

        print(f"Processing cart_details: {len(cart_details)} items")
        print(f"Cart details: {cart_details}")

        if not cart_details:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.BAD_REQUEST,
                message="Cart is empty"
            )

        # Calculate total and prepare order details
        total_price = 0
        order_details = []

        for cart_item in cart_details:
            product_id = cart_item.get('product_id')
            quantity = cart_item.get('quantity', 1)

            # Get product info
            product = get_product(product_id, db)
            if not product or product.status != StatusEnum.SUCCESS:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.NOT_FOUND,
                    message=f"Product {product_id} not found"
                )

            # Check stock
            if product.data.stock < quantity:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.BAD_REQUEST,
                    message=f"Insufficient stock for product {product_id}"
                )

            # Calculate price
            price = product.data.price
            item_total = price * quantity
            total_price += item_total

            order_details.append(OrderDetailCreate(
                product_id=product_id,
                quantity=quantity,
                price=price,
                product_options=""  # Provide empty string instead of None
            ))

        # Create order
        print(f"Creating order with total_price: {total_price}")
        print(f"Order details count: {len(order_details)}")

        order_data = OrderCreate(
            user_id=user_id,
            total_price=total_price,
            order_details=order_details,
            status="pending"
        )

        print(f"Order data created: {order_data}")
        result = create_order(order_data, db)
        print(f"Create order result: {result}")

        if result.status == StatusEnum.SUCCESS:
            # Update cart status to completed
            cart_id = cart_data.get('cart_id')
            if not cart_id and 'cart' in cart_data:
                cart_id = cart_data.get('cart', {}).get('id')

            print(f"Updating cart status for cart_id: {cart_id}")
            if cart_id:
                cart = db.query(Cart).filter(Cart.id == cart_id).first()
                if cart:
                    cart.status = "completed"
                    db.commit()
                    print(f"Cart {cart_id} status updated to completed")
                else:
                    print(f"Cart {cart_id} not found")

        return result

    except Exception as e:
        db.rollback()
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.SERVER_ERROR,
            message=f"Error creating order from cart data: {str(e)}"
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
            code=CodeEnum.SERVER_ERROR,
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
