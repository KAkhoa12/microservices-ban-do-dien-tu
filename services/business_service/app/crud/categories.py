from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from datetime import datetime
import os
from pathlib import Path

from models.categories import Category
from schemas.categories import CategoryCreate, CategoryUpdate
from core.response import Response, StatusEnum, CodeEnum

def get_categories(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    take: int = 10
):
    query = db.query(Category)
    total_categories = query.count()
    categories = query.offset(skip).limit(take).all()
    
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get all categories successfully",
        data={
            "items": categories,
            "total": total_categories,
            "skip": skip,
            "take": take,
            "limit": limit
        }
    )

def get_category(category_id: int, db: Session):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Category not found"
        )
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get category successfully",
        data=category
    )

def get_category_by_slug(slug: str, db: Session):
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Category not found"
        )
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get category successfully",
        data=category
    )

def create_category(category: CategoryCreate, db: Session):
    db_category = Category(
        name=category.name,
        description=category.description,
        slug=category.slug,
        parent_id=category.parent_id,
        created_at=datetime.now().isoformat()
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Category created successfully",
        data=db_category
    )

def update_category(category_id: int, category: CategoryUpdate, db: Session):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Category not found"
        )
    
    update_data = category.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Category updated successfully",
        data=db_category
    )

def update_category_image(category_id: int, image, db: Session):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Category not found"
        )
    if image:
        imgs_dir = Path(__file__).parent.parent / "static" / "imgs" / "categories"
        imgs_dir.mkdir(parents=True, exist_ok=True)
        file_ext = os.path.splitext(image.filename)[1]
        file_name = f"category_{category.id}_{int(datetime.utcnow().timestamp())}{file_ext}"
        file_path = imgs_dir / file_name
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        category.image_url = f"static/imgs/categories/{file_name}"
        db.commit()
        db.refresh(category)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Category image updated successfully",
        data=category
    )

def delete_category(category_id: int, db: Session):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Category not found"
        )
    db.delete(category)
    db.commit()
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Category deleted successfully"
    )

def get_categories_unified(
    skip: int = 0,
    take: int = 10,
    name: Optional[str] = None,
    slug: Optional[str] = None,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = None
):
    query = db.query(Category)
    if category_id is not None:
        query = query.filter(Category.id == category_id)
    if slug is not None:
        query = query.filter(Category.slug == slug)
    if name is not None:
        query = query.filter(Category.name.ilike(f"%{name}%"))
    if search is not None:
        query = query.filter(
            or_(
                Category.name.ilike(f"%{search}%"),
                Category.slug.ilike(f"%{search}%"),
                Category.description.ilike(f"%{search}%")
            )
        )
    total_categories = query.count()
    categories = query.offset(skip).limit(take).all()

    # Calculate pagination info
    page = (skip // take) + 1 if take > 0 else 1
    total_pages = (total_categories + take - 1) // take if take > 0 else 1

    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get categories successfully",
        data={
            "items": categories,  # Changed from "payload" to "items"
            "total": total_categories,
            "page": page,
            "take": take,
            "skip": skip,
            "total_pages": total_pages
        }
    )
