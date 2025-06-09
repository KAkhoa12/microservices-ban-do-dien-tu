from fastapi import APIRouter, Depends, UploadFile, File, Form, Header, Response as FastAPIResponse
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserInDB, UserUpdate, UserUpdateAvatar
from db.database import get_db
from crud import user as crud_user
from crud import token as crud_token
from schemas.user import LoginRequest
from core.response import Response, StatusEnum, CodeEnum
from typing import List, Annotated
from pydantic import BaseModel

# Import các dependencies mới
from decorator.auth import get_current_user_with_response, get_admin_user_with_response

class PaginatedResponse(BaseModel):
    data: List[UserInDB]
    total: int
    skip: int
    take: int
    limit: int

router = APIRouter(prefix="/api/user", tags=["User"])

@router.post("/login")
def login_for_access_token(login_req: LoginRequest, db: Session = Depends(get_db)):
    return crud_user.login_user(login_req, db)

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud_user.register_user(user, db)

@router.get("/me")
def get_current_user(
    current_user = Depends(get_current_user_with_response)
):
    # Kiểm tra nếu current_user là Response (lỗi)
    if hasattr(current_user, 'status'):
        return current_user
    
    # Xóa hashed_password trước khi trả về
    del current_user.hashed_password
    return Response(
        status=StatusEnum.SUCCESS, 
        code=CodeEnum.SUCCESS, 
        message="Get current user successfully", 
        data=current_user
    )

@router.put("/update-info")
def update_user_info(
    info: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_with_response)
):
    # Kiểm tra nếu current_user là Response (lỗi)
    if hasattr(current_user, 'status'):
        return current_user
        
    return crud_user.update_user_info(current_user, info, db)

@router.put("/update-avatar")
def update_user_avatar(
    user_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_with_response)
):
    # Kiểm tra nếu current_user là Response (lỗi)
    if hasattr(current_user, 'status'):
        return current_user

    return crud_user.update_user_avatar(current_user, user_id, image, db)

@router.delete("/admin/delete-user")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_with_response)
):
    # Kiểm tra nếu current_user là Response (lỗi)
    if hasattr(current_user, 'status'):
        return current_user
        
    return crud_user.delete_user(user_id, current_user, db)

@router.get("/admin/list-user")
def get_users(
    skip: int = 0, 
    limit: int = 100,
    take: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user_with_response)
):
    # Kiểm tra nếu current_user là Response (lỗi)
    if hasattr(current_user, 'status'):
        return current_user
        
    return crud_user.get_all_users(current_user, skip, limit, take, db)
@router.get("/validate")
def validate_token_for_kong(
    response: FastAPIResponse,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_with_response)
):
    if hasattr(current_user, 'status'):
        if current_user.status == StatusEnum.ERROR:
            return Response(status=StatusEnum.ERROR,code=CodeEnum.UNAUTHORIZED, message="User not found")
        
    return Response(status=StatusEnum.SUCCESS,code=CodeEnum.SUCCESS, message="User validated successfully")

@router.get("/admin/validate")
def validate_admin_token_for_kong(
    response: FastAPIResponse,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user_with_response)
):

    if hasattr(current_user, 'status'):
        if current_user.status == StatusEnum.ERROR:
            return Response(status=StatusEnum.ERROR,code=CodeEnum.UNAUTHORIZED, message="User not found")
        
    return Response(status=StatusEnum.SUCCESS,code=CodeEnum.SUCCESS, message="Admin validated successfully")
