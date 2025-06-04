from sqlalchemy.orm import Session
from typing import List, Optional
from ..db.models import MomoPayment
from ..schemas.payment import PaymentCreateRequest


def get_payment_by_order_id(db: Session, order_id: str) -> Optional[MomoPayment]:
    """Get payment by order ID"""
    return db.query(MomoPayment).filter(MomoPayment.order_id == order_id).first()


def get_payment_by_request_id(db: Session, request_id: str) -> Optional[MomoPayment]:
    """Get payment by request ID"""
    return db.query(MomoPayment).filter(MomoPayment.request_id == request_id).first()


def get_payments_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[MomoPayment]:
    """Get payments by user ID"""
    return db.query(MomoPayment).filter(MomoPayment.user_id == user_id).offset(skip).limit(limit).all()


def get_payment_by_id(db: Session, payment_id: int) -> Optional[MomoPayment]:
    """Get payment by ID"""
    return db.query(MomoPayment).filter(MomoPayment.id == payment_id).first()


def update_payment_order_created(db: Session, payment_id: int, order_id: int) -> Optional[MomoPayment]:
    """Update payment with created order ID"""
    payment = db.query(MomoPayment).filter(MomoPayment.id == payment_id).first()
    if payment:
        payment.order_created = order_id
        db.commit()
        db.refresh(payment)
    return payment


def get_all_payments(db: Session, skip: int = 0, limit: int = 100) -> List[MomoPayment]:
    """Get all payments with pagination"""
    return db.query(MomoPayment).offset(skip).limit(limit).all()
