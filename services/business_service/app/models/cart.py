from db.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum


class CartStatus(enum.Enum):
    ACTIVE = "active"
    ORDER = "order"


class Cart(Base):
    __tablename__ = "frontend_cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("frontend_user.id"))
    status = Column(Enum(CartStatus), default=CartStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User")
    cart_details = relationship("CartDetail", back_populates="cart", cascade="all, delete-orphan")


class CartDetail(Base):
    __tablename__ = "frontend_cartdetail"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("frontend_cart.id"))
    product_id = Column(Integer, ForeignKey("frontend_product.id"))
    quantity = Column(Integer, default=1)
    product_options = Column(String(255), default="")

    # Relationships
    cart = relationship("Cart", back_populates="cart_details")
    product = relationship("Product")

