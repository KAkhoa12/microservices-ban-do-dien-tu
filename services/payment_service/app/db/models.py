from sqlalchemy import Column, Integer, String, Decimal, DateTime, Text
from sqlalchemy.sql import func
from .database import Base
import uuid


class MomoPayment(Base):
    __tablename__ = "momo_payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True, nullable=False)
    amount = Column(Decimal(10, 0), nullable=False)
    order_info = Column(String(255), nullable=False)
    request_id = Column(String(50), unique=True, index=True, nullable=False)
    transaction_id = Column(String(50), nullable=True)
    message = Column(String(255), nullable=True)
    response_time = Column(DateTime, nullable=True)
    status = Column(String(20), default='pending', nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Additional fields for integration
    user_id = Column(Integer, nullable=True)  # User who made the payment
    cart_data = Column(Text, nullable=True)   # JSON string of cart data
    order_created = Column(Integer, nullable=True)  # Order ID created after successful payment

    @staticmethod
    def generate_order_id():
        return str(uuid.uuid4())

    @staticmethod
    def generate_request_id():
        return str(uuid.uuid4())

    def __repr__(self):
        return f"<MomoPayment(order_id='{self.order_id}', amount={self.amount}, status='{self.status}')>"
