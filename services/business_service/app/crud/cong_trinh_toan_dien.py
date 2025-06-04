from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
import os
from pathlib import Path

from models.cong_trinh_toan_dien import CongTrinhToanDien
from schemas.cong_trinh_toan_dien import CongTrinhToanDienCreate, CongTrinhToanDienUpdate
from core.response import Response, StatusEnum, CodeEnum

def get_cong_trinhs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    take: int = 10
):
    total_cong_trinhs = db.query(CongTrinhToanDien).count()
    cong_trinhs = db.query(CongTrinhToanDien).offset(skip).limit(take).all()
    
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get all cong trinhs successfully",
        data={
            "items": cong_trinhs,
            "total": total_cong_trinhs,
            "skip": skip,
            "take": take,
            "limit": limit
        }
    )

def get_cong_trinh(cong_trinh_id: int, db: Session):
    cong_trinh = db.query(CongTrinhToanDien).filter(CongTrinhToanDien.id == cong_trinh_id).first()
    if not cong_trinh:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Cong trinh not found"
        )
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get cong trinh successfully",
        data=cong_trinh
    )

def get_cong_trinh_by_slug(slug: str, db: Session):
    cong_trinh = db.query(CongTrinhToanDien).filter(CongTrinhToanDien.slug == slug).first()
    if not cong_trinh:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Cong trinh not found"
        )
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get cong trinh successfully",
        data=cong_trinh
    )

def create_cong_trinh(cong_trinh: CongTrinhToanDienCreate, db: Session):
    db_cong_trinh = CongTrinhToanDien(
        title=cong_trinh.title,
        description=cong_trinh.description,
        content=cong_trinh.content,
        created_at=datetime.now()
    )
    db.add(db_cong_trinh)
    db.commit()
    db.refresh(db_cong_trinh)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Cong trinh created successfully",
        data=db_cong_trinh
    )

def update_cong_trinh(cong_trinh_id: int, cong_trinh: CongTrinhToanDienUpdate, db: Session):
    db_cong_trinh = db.query(CongTrinhToanDien).filter(CongTrinhToanDien.id == cong_trinh_id).first()
    if not db_cong_trinh:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Cong trinh not found"
        )
    
    update_data = cong_trinh.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cong_trinh, field, value)
    
    db.commit()
    db.refresh(db_cong_trinh)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Cong trinh updated successfully",
        data=db_cong_trinh
    )

def update_cong_trinh_image(cong_trinh_id: int, image, db: Session):
    cong_trinh = db.query(CongTrinhToanDien).filter(CongTrinhToanDien.id == cong_trinh_id).first()
    if not cong_trinh:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Cong trinh not found"
        )
    if image:
        imgs_dir = Path(__file__).parent.parent / "static" / "imgs" / "cong_trinh"
        imgs_dir.mkdir(parents=True, exist_ok=True)
        file_ext = os.path.splitext(image.filename)[1]
        file_name = f"cong_trinh_{cong_trinh.id}_{int(datetime.now().timestamp())}{file_ext}"
        file_path = imgs_dir / file_name
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        cong_trinh.image_url = f"static/imgs/cong_trinh/{file_name}"
        db.commit()
        db.refresh(cong_trinh)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Cong trinh image updated successfully",
        data=cong_trinh
    )

def delete_cong_trinh(cong_trinh_id: int, db: Session):
    cong_trinh = db.query(CongTrinhToanDien).filter(CongTrinhToanDien.id == cong_trinh_id).first()
    if not cong_trinh:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Cong trinh not found"
        )
    db.delete(cong_trinh)
    db.commit()
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Cong trinh deleted successfully"
    )
