from fastapi import FastAPI, Depends, HTTPException, status, Header, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from jose import jwt, JWTError
import os
from pathlib import Path

from db.database import engine, Base, get_db
from models.user import User
from models.token import Token
from schemas.user import UserBase, UserCreate, UserUpdate, UserInDB
from schemas.token import Token, TokenData, RefreshTokenRequest, VerifyTokenRequest
from core.security import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token,
    get_password_hash, 
    save_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
)
from api import user as user_api
from api import token as token_api

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Service API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files để serve ảnh (thống nhất với các service khác)
app.mount("/static/user", StaticFiles(directory="static"), name="static")

app.include_router(user_api.router)
app.include_router(token_api.router)

