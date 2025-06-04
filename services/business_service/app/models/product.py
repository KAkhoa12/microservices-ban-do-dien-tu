from db.database import Base
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "frontend_product"  

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    old_price = Column(Float)
    tags = Column(Text)
    number_of_sell = Column(Integer, default=0)
    number_of_like = Column(Integer, default=0)
    stock = Column(Integer, default=0)
    image_url = Column(String(255))
    category_id = Column(Integer, ForeignKey("frontend_category.id"))
    brand_id = Column(Integer, ForeignKey("frontend_brand.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    order_details = relationship("OrderDetail", back_populates="product", cascade="all, delete-orphan")


