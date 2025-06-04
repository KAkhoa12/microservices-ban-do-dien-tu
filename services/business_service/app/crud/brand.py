from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.brand import Brand as BrandModel
from fastapi import Depends, Response as FastAPIResponse
from pathlib import Path
import os
from datetime import datetime
from core.response import Response,StatusEnum,CodeEnum
from db.database import get_db
from schemas.brand import Brand, BrandUpdate, BrandCreate
from schemas.auth_user import CurrentUser

def get_list_brand(
    skip: int = 0, 
    limit: int = 100, 
    take: int = 10, 
    db: Session = None):
    
    total_brands = db.query(BrandModel).count()
    brands = db.query(BrandModel).offset(skip).limit(take).all()
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS, 
        message="Get all brands successfully",
        data={
            "items": brands,  # Changed from "payload" to "items"
            "total": total_brands, 
            "skip": skip, 
            "take": take, 
            "limit": limit})

def get_brand_by_id(brand_id: int, db: Session = None):
    brand = db.query(BrandModel).filter(BrandModel.id == brand_id).first()
    return Response(
        status=StatusEnum.SUCCESS, 
        code=CodeEnum.SUCCESS, 
        message="Get brand successfully", 
        data=brand
    )

def get_brand_by_slug(slug: str, db: Session = None):
    brand = db.query(BrandModel).filter(BrandModel.slug == slug).first()
    return Response(
        status=StatusEnum.SUCCESS, 
        code=CodeEnum.SUCCESS, 
        message="Get brand successfully", 
        data=brand
    )
    
def get_brand_by_search(search_key: str, db: Session = None):
    brand = db.query(BrandModel).filter(BrandModel.name.contains(search_key)).all()
    return Response(
        status=StatusEnum.SUCCESS, 
        code=CodeEnum.SUCCESS, 
        message="Get brand successfully", 
        data=brand
    )

def update_brand_info(brand_info:BrandUpdate,db: Session = None):
    brand = db.query(BrandModel).filter(BrandModel.id == brand_info.id).first()
    if not brand:
        return Response(
            status=StatusEnum.ERROR, 
            code=CodeEnum.NOT_FOUND, 
            message="Brand not found"
        )
    brand.name = brand_info.name
    brand.slug = brand_info.slug
    db.commit()
    db.refresh(brand)
    return Response(
        status=StatusEnum.SUCCESS, 
        code=CodeEnum.SUCCESS, 
        message="Update brand successfully", 
        data=brand
    )


def update_brand_avatar(brand_id, image, db: Session):
    brand = db.query(BrandModel).filter(BrandModel.id == brand_id).first()
    if not brand:
        return Response(
            status=StatusEnum.ERROR, 
            code=CodeEnum.NOT_FOUND, 
            message="Brand not found")
    if image:
        imgs_dir = Path(__file__).parent.parent / "static" / "imgs" / "brands"
        imgs_dir.mkdir(parents=True, exist_ok=True)
        file_ext = os.path.splitext(image.filename)[1]
        file_name = f"brand_{brand.id}_{int(datetime.utcnow().timestamp())}{file_ext}"
        file_path = imgs_dir / file_name
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        brand.image = f"static/imgs/brands/{file_name}"
        db.commit()
        db.refresh(brand)
    return Response(status=StatusEnum.SUCCESS, code=CodeEnum.SUCCESS, message="brand updated successfully", data=brand)

def delete_brand(brand_id, db: Session):
    brand = db.query(BrandModel).filter(BrandModel.id == brand_id).first()
    if not brand:
        return Response(
            status=StatusEnum.ERROR, 
            code=CodeEnum.NOT_FOUND, 
            message="Brand not found")
    db.delete(brand)
    db.commit()
    return Response(
        status=StatusEnum.SUCCESS, 
        code=CodeEnum.SUCCESS, 
        message="Brand deleted successfully")

def create_brand(brand: BrandCreate, db: Session = None):
    new_brand = Brand(**brand.model_dump())
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Brand created successfully",
        data=new_brand)

def get_brands_unified(
    skip: int = 0,
    take: int = 10,
    name: Optional[str] = None,
    slug: Optional[str] = None,
    search: Optional[str] = None,
    brand_id: Optional[int] = None,
    db: Session = None
):
    query = db.query(BrandModel)
    if brand_id is not None:
        query = query.filter(BrandModel.id == brand_id)
    if slug is not None:
        query = query.filter(BrandModel.slug == slug)
    if name is not None:
        query = query.filter(BrandModel.name.ilike(f"%{name}%"))
    if search is not None:
        query = query.filter(
            or_(
                BrandModel.name.ilike(f"%{search}%"),
                BrandModel.slug.ilike(f"%{search}%")
            )
        )
    total_brands = query.count()
    brands = query.offset(skip).limit(take).all()

    # Calculate pagination info
    page = (skip // take) + 1 if take > 0 else 1
    total_pages = (total_brands + take - 1) // take if take > 0 else 1

    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get brands successfully",
        data={
            "items": brands,  # Changed from "payload" to "items"
            "total": total_brands,
            "page": page,
            "take": take,
            "skip": skip,
            "total_pages": total_pages
        }
    )