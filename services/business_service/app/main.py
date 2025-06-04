from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path

from db.database import *
Base.metadata.create_all(engine)

from api import giai_phap_am_thanh, cong_trinh_toan_dien, brand, categories, product, cart, order
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Business Service API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files để serve ảnh
app.mount("/static/business", StaticFiles(directory="static"), name="static")

# Mount uploads directory để serve uploaded files
uploads_dir = Path("static/uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads/business_service", StaticFiles(directory="static/uploads"), name="uploads")

app.include_router(
    brand.router, 
    prefix="/api/brand", 
    tags=["Brand"])

app.include_router(
    giai_phap_am_thanh.router, 
    prefix="/api/giai-phap-am-thanh", 
    tags=["Giai Phap Am Thanh"])

app.include_router(
    cong_trinh_toan_dien.router, 
    prefix="/api/cong-trinh-toan-dien", 
    tags=["Cong Trinh Toan Dien"])
app.include_router(
    categories.router, 
    prefix="/api/category", 
    tags=["Categories"])
app.include_router(
    product.router,
    prefix="/api/product",
    tags=["Product"])

app.include_router(
    cart.router,
    prefix="/api/cart",
    tags=["Cart"])

app.include_router(
    order.router,
    prefix="/api/order",
    tags=["Order"])
