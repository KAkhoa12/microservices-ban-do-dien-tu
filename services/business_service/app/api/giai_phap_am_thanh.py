from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from db.database import get_db
from crud.giai_phap_am_thanh import *
from schemas.giai_phap_am_thanh import GiaiPhapAmThanhCreate, GiaiPhapAmThanhUpdate

router = APIRouter()

@router.get("/list-giai-phap")
def api_get_giai_phaps(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_giai_phaps(db, skip, limit)

@router.get("/get-giai-phap-id")
def api_get_giai_phap(giai_phap_id: int, db: Session = Depends(get_db)):
    return get_giai_phap(giai_phap_id, db)

@router.post("/create-giai-phap")
def api_create_giai_phap(
    giai_phap: GiaiPhapAmThanhCreate,
    db: Session = Depends(get_db)
):
    return create_giai_phap(giai_phap, db)

@router.put("/update-giai-phap")
def api_update_giai_phap(
    giai_phap_id: int,
    giai_phap: GiaiPhapAmThanhUpdate,
    db: Session = Depends(get_db)
):
    return update_giai_phap(giai_phap_id, giai_phap, db)

@router.put("/update-giai-phap-image")
def api_update_giai_phap_image(
    giai_phap_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return update_giai_phap_image(giai_phap_id, image, db)

@router.delete("/delete-giai-phap")
def api_delete_giai_phap(giai_phap_id: int, db: Session = Depends(get_db)):
    return delete_giai_phap(giai_phap_id, db)
