from sqlalchemy.orm import Session
from models.user import User
from core.security import get_password_hash
from fastapi import Depends, Response as FastAPIResponse
from pathlib import Path
import os
from datetime import datetime
from core.response import Response,StatusEnum,CodeEnum
from db.database import get_db
from schemas.user import UserInDB, UserUpdate
from core.security import authenticate_user, create_access_token, create_refresh_token, save_token
from schemas.user import LoginRequest, RegisterRequest

def login_user(login_req: LoginRequest, db: Session):
    user = authenticate_user(db, login_req.username, login_req.password)
    if not user:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.BAD_REQUEST,
            message="Incorrect username or password"
        )
    access_token, access_expires_at = create_access_token(
        data={
            "sub": user.username,
            "user_role": user.user_role
        }
    )
    refresh_token, refresh_expires_at = create_refresh_token(
        data={"sub": user.username}
    )
    save_token(db, user.id, access_token, refresh_token, access_expires_at, refresh_expires_at)
    expires_in = int((access_expires_at - datetime.utcnow()).total_seconds())
    refresh_expires_in = int((refresh_expires_at - datetime.utcnow()).total_seconds())
    return Response(
        status=StatusEnum.SUCCESS,code=CodeEnum.SUCCESS,
        message="Login successful",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
            "refresh_expires_in": refresh_expires_in
        })

def register_user(user:RegisterRequest, db: Session):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        return Response(
            status=StatusEnum.ERROR, 
            code=CodeEnum.BAD_REQUEST, 
            message="Username or email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        image='static/imgs/default.png',
        user_role= 'customer'
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    del db_user.hashed_password
    return Response(
        status=StatusEnum.SUCCESS, 
        code=CodeEnum.SUCCESS, 
        message="User registered successfully", 
        data=db_user)

def update_user_info(current_user:UserInDB, info:UserUpdate, db: Session):
    print("Thông tin user:", current_user)
    # Kiểm tra quyền truy cập
    if current_user.id != info.id and current_user.user_role != "admin":
        return Response(status=StatusEnum.ERROR, code=CodeEnum.FORBIDDEN, message="Permission denied")

    # Lấy user cần update
    if current_user.user_role == "admin" and info.id != current_user.id:
        # Admin update user khác
        user = db.query(User).filter(User.id == info.id).first()
        if not user:
            return Response(status=StatusEnum.ERROR, code=CodeEnum.NOT_FOUND, message="User not found")
    else:
        # User update chính mình hoặc admin update chính mình
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            return Response(status=StatusEnum.ERROR, code=CodeEnum.NOT_FOUND, message="User not found")

    # Cập nhật thông tin
    if info.full_name:
        user.full_name = info.full_name
    if info.email:
        user.email = info.email
    if info.phone_number:
        user.phone_number = info.phone_number
    if info.address:
        user.address = info.address

    # Chỉ admin mới được cập nhật user_role và is_delete
    if current_user.user_role == "admin":
        if info.user_role:
            user.user_role = info.user_role
        if info.is_delete is not None:
            user.is_delete = 1 if info.is_delete else 0

    db.commit()
    db.refresh(user)
    del user.hashed_password
    return Response(status=StatusEnum.SUCCESS, code=CodeEnum.SUCCESS, message="User updated successfully", data=user)

def update_user_avatar(current_user, user_id, image, db: Session):
    # Kiểm tra quyền: user chỉ có thể update avatar của chính mình, admin có thể update bất kỳ ai
    if current_user.user_role != "admin" and current_user.id != user_id:
        return Response(status=StatusEnum.ERROR, code=CodeEnum.FORBIDDEN, message="Permission denied")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return Response(status=StatusEnum.ERROR, code=CodeEnum.NOT_FOUND, message="User not found")
    if image:
        # Use static directory that's mapped to host via Docker volumes (consistent with other services)
        static_dir = Path(__file__).parent.parent / "static" / "imgs" / "avatars"
        static_dir.mkdir(parents=True, exist_ok=True)

        file_ext = os.path.splitext(image.filename)[1]
        file_name = f"user_{user.id}_{int(datetime.utcnow().timestamp())}{file_ext}"
        file_path = static_dir / file_name

        # Save file to static directory
        with open(file_path, "wb") as f:
            f.write(image.file.read())

        # Store relative path in database (accessible via Kong gateway)
        user.image = f"static/imgs/avatars/{file_name}"
        db.commit()
        db.refresh(user)
    return Response(status=StatusEnum.SUCCESS, code=CodeEnum.SUCCESS, message="User updated successfully", data=user)

def delete_user(user_id, current_user, db: Session):
    if current_user.user_role != "admin" and current_user.id != user_id:
        return Response(status=StatusEnum.ERROR, code=CodeEnum.FORBIDDEN, message="Permission denied")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return Response(status=StatusEnum.ERROR, code=CodeEnum.NOT_FOUND, message="User not found")
    
    user.is_delete = 1
    db.commit()
    return Response(status=StatusEnum.SUCCESS, code=CodeEnum.SUCCESS, message="User deleted successfully")

def get_all_users(current_user:UserInDB, skip: int = 0, limit: int = 100, take: int = 10, db: Session = None):
    if current_user and hasattr(current_user, 'user_role'):
        if current_user.user_role != "admin":
            return Response(status=StatusEnum.ERROR, code=CodeEnum.FORBIDDEN, message="Permission denied")
    total_users = db.query(User).filter(User.is_delete == 0).count()
    users = db.query(User).filter(User.is_delete == 0).offset(skip).limit(take).all()
    for user in users:
        del user.hashed_password
    return Response(status=StatusEnum.SUCCESS,code=CodeEnum.SUCCESS, message="Get all users successfully",data={"users": users, "total": total_users, "skip": skip, "take": take, "limit": limit})
def validate_user(current_user:UserInDB,response:FastAPIResponse, db: Session = None):
    return Response(status=StatusEnum.SUCCESS,code=CodeEnum.SUCCESS, message="User validated successfully")
