from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from db.database import get_db
from crud.brand import *
from schemas.brand import BrandCreate, BrandUpdate

router = APIRouter()

@router.get("/brands")
def api_get_brands(
    page: int = 1,
    take: int = 10,
    skip: Optional[int] = None,  # Keep for backward compatibility
    name: Optional[str] = None,
    slug: Optional[str] = None,
    search: Optional[str] = None,
    brand_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    # Calculate skip from page if skip is not provided
    if skip is None:
        skip = (page - 1) * take
    return get_brands_unified(skip, take, name, slug, search, brand_id, db)

@router.post("/create-brand")
def api_create_brand(brand: BrandCreate, db: Session = Depends(get_db)):
    return create_brand(brand, db)

@router.put("/update-info")
def api_update_brand_info(brand_info: BrandUpdate, db: Session = Depends(get_db)):
    return update_brand_info(brand_info, db)

@router.put("/update-avatar")
def api_update_brand_avatar(
    brand_id: int, 
    image: UploadFile = File(...), 
    db: Session = Depends(get_db)):
    return update_brand_avatar(brand_id, image, db)

@router.delete("/delete-brand")
def api_delete_brand(brand_id: int, db: Session = Depends(get_db)):
    return delete_brand(brand_id, db)