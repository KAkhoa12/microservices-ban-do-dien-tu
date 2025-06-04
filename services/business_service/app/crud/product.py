from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException
from datetime import datetime
import os
from pathlib import Path

from models.product import Product
from schemas.product import ProductCreate, ProductUpdate
from core.response import Response, StatusEnum, CodeEnum

def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    take: int = 10,
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None
):
    query = db.query(Product)
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if brand_id is not None:
        query = query.filter(Product.brand_id == brand_id)
    
    total_products = query.count()
    products = query.offset(skip).limit(take).all()
    
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get all products successfully",
        data={
            "items": products,
            "total": total_products,
            "skip": skip,
            "take": take,
            "limit": limit
        }
    )

def get_product(product_id: int, db: Session):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Product not found"
        )
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get product successfully",
        data=product
    )

def create_product(product: ProductCreate, db: Session):
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        old_price=product.old_price,
        brand_id=product.brand_id,
        tags=product.tags,
        number_of_sell=product.number_of_sell,
        number_of_like=product.number_of_like,
        category_id=product.category_id,
        stock=product.stock,
        created_at=datetime.now()
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Product created successfully",
        data=db_product
    )

def update_product(product_id: int, product: ProductUpdate, db: Session):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Product not found"
        )
    
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Product updated successfully",
        data=db_product
    )

def update_product_image(product_id: int, image, db: Session):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Product not found"
        )
    if image:
        imgs_dir = Path(__file__).parent.parent / "static" / "imgs" / "products"
        imgs_dir.mkdir(parents=True, exist_ok=True)
        file_ext = os.path.splitext(image.filename)[1]
        file_name = f"product_{product.id}_{int(datetime.utcnow().timestamp())}{file_ext}"
        file_path = imgs_dir / file_name
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        product.image_url = f"static/imgs/products/{file_name}"
        db.commit()
        db.refresh(product)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Product image updated successfully",
        data=product
    )

def delete_product(product_id: int, db: Session):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Product not found"
        )
    db.delete(product)
    db.commit()
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Product deleted successfully"
    )

def update_product_stock(product_id: int, quantity: int, db: Session):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Product not found"
        )
    
    if product.stock < quantity:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.BAD_REQUEST,
            message="Insufficient stock"
        )
    
    product.stock -= quantity
    db.commit()
    db.refresh(product)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Product stock updated successfully",
        data=product
    )

def get_products_unified(
    skip: int = 0,
    take: int = 10,
    name: Optional[str] = None,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    product_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = None
):
    query = db.query(Product)
    if product_id is not None:
        query = query.filter(Product.id == product_id)
    if name is not None:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if search is not None:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if brand_id is not None:
        query = query.filter(Product.brand_id == brand_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    total_products = query.count()
    products = query.offset(skip).limit(take).all()

    # Calculate pagination info
    page = (skip // take) + 1 if take > 0 else 1
    total_pages = (total_products + take - 1) // take if take > 0 else 1

    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get products successfully",
        data={
            "items": products,  # Changed from "payload" to "items"
            "total": total_products,
            "page": page,
            "take": take,
            "skip": skip,
            "total_pages": total_pages
        }
    )
