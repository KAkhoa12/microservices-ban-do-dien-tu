from fastapi import Depends, Header
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import Annotated
from db.database import get_db
from models.user import User
from core.security import SECRET_KEY, ALGORITHM
from core.response import Response, StatusEnum, CodeEnum
from schemas.user import UserInDB

def get_current_user_with_response(
    authorization: Annotated[str, Header(alias="Authorization")] = None,
    db: Session = Depends(get_db)
):
    """
    Dependency để lấy current user từ JWT token
    Trả về User object hoặc Response object nếu có lỗi
    """
    
    if not authorization or not authorization.startswith("Bearer "):
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.UNAUTHORIZED,
            message="Invalid or missing authorization header"
        )
    
    try:
        token = authorization.split(" ", 1)[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_role: str = payload.get("user_role")
        
        if username is None:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.UNAUTHORIZED,
                message="Invalid token payload"
            )
            
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.NOT_FOUND,
                message="User not found"
            )
        
        # Cập nhật user_role từ token nếu có
        user.user_role = user_role or user.user_role
        print("gốc: ", user)
        return user
        
    except JWTError:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.UNAUTHORIZED,
            message="Invalid access token"
        )
    except Exception as e:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.INTERNAL_SERVER_ERROR,
            message=f"Internal server error: {str(e)}"
        )

def get_admin_user_with_response(
    current_user = Depends(get_current_user_with_response)
):
    if hasattr(current_user, 'status'):
        return current_user
    if current_user.user_role != "admin":
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.FORBIDDEN,
            message="Permission denied: Admins only"
        )
    return current_user