from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path

from db.database import *
Base.metadata.create_all(engine)

from api.v1.endpoints import chatbot
from api.v1.endpoints import data_management

app = FastAPI(title="Chatbot Service API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files để serve ảnh
app.mount("/static/chatbot", StaticFiles(directory="assets"), name="static")

# Mount uploads directory để serve uploaded files
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads/chatbot_service", StaticFiles(directory="uploads"), name="uploads")

app.include_router(
    chatbot.router,
    prefix="/api/chatbot",
    tags=["Chatbot"])

app.include_router(
    data_management.router,
    prefix="/api/chatbot/data",
    tags=["Data Management"])

@app.get("/")
def read_root():
    return {"message": "Chatbot Service API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}