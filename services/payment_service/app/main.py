from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .api.v1 import payment
from .db.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Payment Service",
    description="Microservice for handling payments (MoMo, etc.)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(payment.router, prefix="/api/payment", tags=["payment"])

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Payment Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment_service"}