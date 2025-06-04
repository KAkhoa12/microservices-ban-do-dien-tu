from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from db.database import get_db
from crud.cong_trinh_toan_dien import *
from schemas.cong_trinh_toan_dien import CongTrinhToanDienCreate, CongTrinhToanDienUpdate

router = APIRouter()

@router.get("/list-cong-trinh")
def api_get_cong_trinhs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_cong_trinhs(db, skip, limit)

@router.get("/get-cong-trinh-id")
def api_get_cong_trinh(cong_trinh_id: int, db: Session = Depends(get_db)):
    return get_cong_trinh(cong_trinh_id, db)

@router.post("/create-cong-trinh")
def api_create_cong_trinh(
    cong_trinh: CongTrinhToanDienCreate,
    db: Session = Depends(get_db)
):
    return create_cong_trinh(cong_trinh, db)

@router.put("/update-cong-trinh")
def api_update_cong_trinh(
    cong_trinh_id: int,
    cong_trinh: CongTrinhToanDienUpdate,
    db: Session = Depends(get_db)
):
    return update_cong_trinh(cong_trinh_id, cong_trinh, db)

@router.put("/update-cong-trinh-image")
def api_update_cong_trinh_image(
    cong_trinh_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return update_cong_trinh_image(cong_trinh_id, image, db)

@router.delete("/delete-cong-trinh")
def api_delete_cong_trinh(cong_trinh_id: int, db: Session = Depends(get_db)):
    return delete_cong_trinh(cong_trinh_id, db)
