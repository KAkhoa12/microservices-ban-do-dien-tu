from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.token import Token, RefreshTokenRequest, VerifyTokenRequest
from db.database import get_db
from crud import token as crud_token

router = APIRouter()


@router.post("/token/refresh")
def refresh_access_token(refresh_req: RefreshTokenRequest, db: Session = Depends(get_db)):
    return crud_token.refresh_access_token(refresh_req, db)


@router.post("/token/verify")
def verify_token_api(verify_req: VerifyTokenRequest, db: Session = Depends(get_db)):
    return crud_token.verify_token_api(verify_req, db)
