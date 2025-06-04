from fastapi import Depends, Header
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import Annotated, Optional
from db.database import get_db
from models.user import User
from core.security import SECRET_KEY, ALGORITHM
from core.response import Response, StatusEnum, CodeEnum
from schemas.auth_user import CurrentUser

def get_current_user_from_kong(
    x_user_id: Annotated[str, Header(alias="x-user-id")] = None,
    x_username: Annotated[str, Header(alias="x-username")] = None,
    x_user_role: Annotated[str, Header(alias="x-user-role")] = None,
    x_email: Annotated[str, Header(alias="x-email")] = None,
    x_full_name: Annotated[str, Header(alias="x-full-name")] = None,
):
    if not x_user_id or not x_username:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.UNAUTHORIZED,
            message="User information not found in headers. Authentication required."
        )
    
    try:
        return Response(
            status=StatusEnum.SUCCESS,
            code=CodeEnum.SUCCESS,
            message="User information found in headers",
            data=CurrentUser(
                user_id=int(x_user_id),
                username=x_username,
                user_role=x_user_role,
                email=x_email,
                full_name=x_full_name
            )
        )
    except ValueError as e:
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.UNAUTHORIZED,
            message=str(e)
        )
        
def require_admin_from_kong(
    current_user: CurrentUser = Depends(get_current_user_from_kong)
) -> CurrentUser:
    """
    Dependency để kiểm tra admin role từ Kong headers
    """
    
    if current_user.user_role != "admin":
        return Response(
            status=StatusEnum.ERROR,
            code=CodeEnum.FORBIDDEN,
            message="Permission denied: Admins only"
        )
    
    return Response(
        status=StatusEnum.SUCCESS,
        code=CodeEnum.SUCCESS,
        message="User is an admin",
        data=current_user
    )

def get_optional_user_from_kong(
    x_user_id: Annotated[str, Header(alias="x-user-id")] = None,
    x_username: Annotated[str, Header(alias="x-username")] = None,
    x_user_role: Annotated[str, Header(alias="x-user-role")] = None,
    x_email: Annotated[str, Header(alias="x-email")] = None,
    x_full_name: Annotated[str, Header(alias="x-full-name")] = None,
) -> Optional[CurrentUser]:
    """
    Optional dependency - trả về None nếu không có auth headers
    Dùng cho các endpoint có thể access mà không cần login
    """
    
    if not x_user_id or not x_username:
        return None
    
    try:
        return Response(
            status=StatusEnum.SUCCESS,
            code=CodeEnum.SUCCESS,
            message="User information found in headers",
            data=CurrentUser(
                user_id=int(x_user_id),
                username=x_username,
                user_role=x_user_role,
                email=x_email,
                full_name=x_full_name
            )
        )
    except ValueError:
        return None
