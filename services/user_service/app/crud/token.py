from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from jose import jwt, JWTError
from models.user import User
from models.token import Token as TokenModel
from core.security import authenticate_user, create_access_token, create_refresh_token, save_token, SECRET_KEY, ALGORITHM
from core.response import Response, StatusEnum,CodeEnum
from schemas.token import Token

def refresh_access_token(refresh_req, db: Session):
    refresh_token = refresh_req.refresh_token
    token_record = db.query(TokenModel).filter(TokenModel.refresh_token == refresh_token).first()
    if not token_record:
        return Response(status=StatusEnum.ERROR,code=CodeEnum.BAD_REQUEST, message="Invalid refresh token")
    if token_record.refresh_expires_at < datetime.utcnow():
        return Response(status=StatusEnum.ERROR,code=CodeEnum.BAD_REQUEST, message="Refresh token expired")
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return Response(status=StatusEnum.ERROR,code=CodeEnum.BAD_REQUEST, message="Invalid token payload")
    except JWTError:
        return Response(status=StatusEnum.ERROR,code=CodeEnum.BAD_REQUEST, message="Invalid refresh token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return Response(status=StatusEnum.ERROR,code=CodeEnum.BAD_REQUEST, message="User not found")
    access_token, access_expires_at = create_access_token(data={"sub": user.username, "user_role": user.user_role})
    token_record.access_token = access_token
    token_record.access_expires_at = access_expires_at
    db.commit()
    expires_in = int((access_expires_at - datetime.utcnow()).total_seconds())
    refresh_expires_in = int((token_record.refresh_expires_at - datetime.utcnow()).total_seconds())
    return Response(status=StatusEnum.SUCCESS,code=CodeEnum.SUCCESS, message="Refresh token successful",data={"access_token": access_token, "refresh_token": refresh_token, "expires_in": expires_in, "refresh_expires_in": refresh_expires_in})

def verify_token_api(verify_req, db: Session):
    access_token = verify_req.access_token
    refresh_token = verify_req.refresh_token
    token_record = db.query(TokenModel).filter(TokenModel.refresh_token == refresh_token).first()
    if not token_record:
        return Response(status=StatusEnum.ERROR,code=CodeEnum.BAD_REQUEST, message="Invalid refresh token")
    if token_record.refresh_expires_at < datetime.utcnow():
        return Response(status=StatusEnum.ERROR,code=CodeEnum.BAD_REQUEST, message="Refresh token expired")
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_role: str = payload.get("user_role")
        if username is None:
            return Response(status=StatusEnum.ERROR,code=CodeEnum.BAD_REQUEST, message="Invalid token payload")
        expires_in = int((token_record.access_expires_at - datetime.utcnow()).total_seconds())
        refresh_expires_in = int((token_record.refresh_expires_at - datetime.utcnow()).total_seconds())
        return Response(status=StatusEnum.SUCCESS,code=CodeEnum.SUCCESS, message="Verify token successful",data={"access_token": access_token, "refresh_token": refresh_token, "expires_in": expires_in, "refresh_expires_in": refresh_expires_in, "user_role": user_role}),None
    except JWTError:
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            user_role: str = payload.get("user_role")
            if username is None:
                return Response(status=StatusEnum.ERROR,code=CodeEnum.BAD_REQUEST, message="Invalid token payload")
        except JWTError:
            return Response(status=StatusEnum.ERROR,code=CodeEnum.BAD_REQUEST, message="Invalid refresh token")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return Response(status=StatusEnum.ERROR,code=CodeEnum.BAD_REQUEST, message="User not found")
        new_access_token, access_expires_at = create_access_token(data={"sub": user.username, "user_role": user.user_role})
        token_record.access_token = new_access_token
        token_record.access_expires_at = access_expires_at
        db.commit()
        expires_in = int((access_expires_at - datetime.utcnow()).total_seconds())
        refresh_expires_in = int((token_record.refresh_expires_at - datetime.utcnow()).total_seconds())
        return Response(status=StatusEnum.SUCCESS,code=CodeEnum.SUCCESS, message="Verify token successful",data={"access_token": new_access_token, "refresh_token": refresh_token, "expires_in": expires_in, "refresh_expires_in": refresh_expires_in, "user_role": user.user_role})
