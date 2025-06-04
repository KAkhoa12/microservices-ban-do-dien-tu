from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.chat import (
    ChatRequest, 
    ProductInfoRequest, 
    CompareProductsRequest, 
    TopProductsRequest
)
from crud.chat import ChatCRUD
from crud.product_operations import ProductOperationsCRUD

router = APIRouter()

# Initialize CRUD instances
chat_crud = ChatCRUD()
product_crud = ProductOperationsCRUD()

@router.post("/chat")
def chat_with_ai(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat với AI Agent
    """
    return chat_crud.process_chat(db, chat_request)

@router.get("/history/{session_id}")
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Lấy lịch sử chat của session
    """
    return chat_crud.get_session_history(db, session_id)

@router.post("/product-info")
def get_product_info(
    request: ProductInfoRequest,
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin chi tiết sản phẩm
    """
    return product_crud.get_product_info(db, request.product_identifier)

@router.post("/compare-products")
def compare_products(
    request: CompareProductsRequest,
    db: Session = Depends(get_db)
):
    """
    So sánh hai sản phẩm
    """
    return product_crud.compare_products(
        db, 
        request.product1_identifier, 
        request.product2_identifier
    )

@router.post("/top-selling")
def get_top_selling_products(
    request: TopProductsRequest,
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách sản phẩm bán chạy nhất
    """
    return product_crud.get_top_selling_products(db, request.limit)

@router.post("/top-liked")
def get_top_liked_products(
    request: TopProductsRequest,
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách sản phẩm được yêu thích nhất
    """
    return product_crud.get_top_liked_products(db, request.limit)

@router.post("/least-selling")
def get_least_selling_products(
    request: TopProductsRequest,
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách sản phẩm bán ít nhất
    """
    return product_crud.get_least_selling_products(db, request.limit)

@router.get("/verify-product/{product_identifier}")
def verify_product(
    product_identifier: str,
    db: Session = Depends(get_db)
):
    """
    Kiểm tra sản phẩm có tồn tại không
    """
    return product_crud.verify_product(db, product_identifier)
