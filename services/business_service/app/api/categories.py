from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from db.database import get_db
from crud.categories import *
from schemas.categories import CategoryCreate, CategoryUpdate

router = APIRouter()

@router.get("/categories")
def api_get_categories(
    page: int = 1,
    take: int = 10,
    skip: Optional[int] = None,  # Keep for backward compatibility
    name: Optional[str] = None,
    slug: Optional[str] = None,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    # Calculate skip from page if skip is not provided
    if skip is None:
        skip = (page - 1) * take
    return get_categories_unified(skip, take, name, slug, search, category_id, db)

@router.post("/create-category")
def api_create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(category, db)

@router.put("/update-category")
def api_update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):
    return update_category(category_id, category, db)

@router.put("/update-category-image")
def api_update_category_image(
    category_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return update_category_image(category_id, image, db)

@router.delete("/delete-category")
def api_delete_category(category_id: int, db: Session = Depends(get_db)):
    return delete_category(category_id, db)