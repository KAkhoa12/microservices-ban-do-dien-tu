from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from db.database import get_db
from crud.product import *
from schemas.product import ProductCreate, ProductUpdate

router = APIRouter()

@router.get("/products")
def api_get_products(
    page: int = 1,
    take: int = 10,
    skip: Optional[int] = None,  # Keep for backward compatibility
    name: Optional[str] = None,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    product_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    # Calculate skip from page if skip is not provided
    if skip is None:
        skip = (page - 1) * take
    return get_products_unified(skip, take, name, search, category_id, brand_id, product_id, min_price, max_price, db)

@router.post("/create-product")
def api_create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return create_product(product, db)

@router.put("/update-product")
def api_update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    return update_product(product_id, product, db)

@router.put("/update-product-image")
def api_update_product_image(
    product_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return update_product_image(product_id, image, db)

@router.delete("/delete-product")
def api_delete_product(product_id: int, db: Session = Depends(get_db)):
    return delete_product(product_id, db)
