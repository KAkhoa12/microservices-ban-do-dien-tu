from sqlalchemy import Column, Integer, Float, String, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from db.database import Base

class Order(Base):
    __tablename__ = "frontend_order"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("frontend_user.id"))
    total_price = Column(Float)
    status = Column(String(10), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order", cascade="all, delete-orphan")

class OrderDetail(Base):
    __tablename__ = "frontend_orderdetail"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("frontend_order.id"))
    product_id = Column(Integer, ForeignKey("frontend_product.id"))
    product_options = Column(Text)
    quantity = Column(Integer)
    price = Column(Float)

    # Relationships
    order = relationship("Order", back_populates="order_details")
    product = relationship("Product")