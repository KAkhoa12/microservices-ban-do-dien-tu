from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
import os
from pathlib import Path

from models.giai_phap_am_thanh import GiaiPhapAmThanh
from schemas.giai_phap_am_thanh import GiaiPhapAmThanhCreate, GiaiPhapAmThanhUpdate
from core.response import Response, StatusEnum, CodeEnum

def get_giai_phaps(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    take: int = 10
):
    total_giai_phaps = db.query(GiaiPhapAmThanh).count()
    giai_phaps = db.query(GiaiPhapAmThanh).offset(skip).limit(take).all()
    
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get all giai phaps successfully",
        data={
            "items": giai_phaps,
            "total": total_giai_phaps,
            "skip": skip,
            "take": take,
            "limit": limit
        }
    )

def get_giai_phap(giai_phap_id: int, db: Session):
    giai_phap = db.query(GiaiPhapAmThanh).filter(GiaiPhapAmThanh.id == giai_phap_id).first()
    if not giai_phap:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Giai phap not found"
        )
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get giai phap successfully",
        data=giai_phap
    )

def get_giai_phap_by_slug(slug: str, db: Session):
    giai_phap = db.query(GiaiPhapAmThanh).filter(GiaiPhapAmThanh.slug == slug).first()
    if not giai_phap:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Giai phap not found"
        )
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Get giai phap successfully",
        data=giai_phap
    )

def create_giai_phap(giai_phap: GiaiPhapAmThanhCreate, db: Session):
    db_giai_phap = GiaiPhapAmThanh(
        title=giai_phap.title,
        description=giai_phap.description,
        content=giai_phap.content,
        created_at=datetime.now()
    )
    db.add(db_giai_phap)
    db.commit()
    db.refresh(db_giai_phap)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Giai phap created successfully",
        data=db_giai_phap
    )

def update_giai_phap(giai_phap_id: int, giai_phap: GiaiPhapAmThanhUpdate, db: Session):
    db_giai_phap = db.query(GiaiPhapAmThanh).filter(GiaiPhapAmThanh.id == giai_phap_id).first()
    if not db_giai_phap:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Giai phap not found"
        )
    
    update_data = giai_phap.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_giai_phap, field, value)
    
    db.commit()
    db.refresh(db_giai_phap)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Giai phap updated successfully",
        data=db_giai_phap
    )

def update_giai_phap_image(giai_phap_id: int, image, db: Session):
    giai_phap = db.query(GiaiPhapAmThanh).filter(GiaiPhapAmThanh.id == giai_phap_id).first()
    if not giai_phap:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Giai phap not found"
        )
    if image:
        imgs_dir = Path(__file__).parent.parent / "static" / "imgs" / "giai_phap"
        imgs_dir.mkdir(parents=True, exist_ok=True)
        file_ext = os.path.splitext(image.filename)[1]
        file_name = f"giai_phap_{giai_phap.id}_{int(datetime.now().timestamp())}{file_ext}"
        file_path = imgs_dir / file_name
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        giai_phap.image_url = f"static/business/imgs/giai_phap/{file_name}"
        db.commit()
        db.refresh(giai_phap)
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Giai phap image updated successfully",
        data=giai_phap
    )

def delete_giai_phap(giai_phap_id: int, db: Session):
    giai_phap = db.query(GiaiPhapAmThanh).filter(GiaiPhapAmThanh.id == giai_phap_id).first()
    if not giai_phap:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.NOT_FOUND,
            message="Giai phap not found"
        )
    db.delete(giai_phap)
    db.commit()
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="Giai phap deleted successfully"
    )
