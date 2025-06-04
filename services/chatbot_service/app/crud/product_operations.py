from typing import Optional
from sqlalchemy.orm import Session

from core.response import Response, StatusEnum, CodeEnum
from utils.aiagent_integration import AIAgentIntegration

class ProductOperationsCRUD:
    def __init__(self):
        self.ai_integration = AIAgentIntegration()
    
    def get_product_info(self, db: Session, product_identifier: str) -> Response:
        """Lấy thông tin chi tiết sản phẩm"""
        try:
            rag_handler = self.ai_integration.get_rag_handler()
            if not rag_handler:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.INTERNAL_SERVER_ERROR,
                    message="Không thể khởi tạo RAG Handler"
                )
            
            product_info = rag_handler.get_product_by_name_or_id(product_identifier)
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="Lấy thông tin sản phẩm thành công",
                data={
                    "product_info": product_info
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi lấy thông tin sản phẩm: {str(e)}"
            )
    
    def compare_products(self, db: Session, product1_identifier: str, product2_identifier: str) -> Response:
        """So sánh hai sản phẩm"""
        try:
            rag_handler = self.ai_integration.get_rag_handler()
            if not rag_handler:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.INTERNAL_SERVER_ERROR,
                    message="Không thể khởi tạo RAG Handler"
                )
            
            comparison_result = rag_handler.compare_products(product1_identifier, product2_identifier)
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="So sánh sản phẩm thành công",
                data={
                    "comparison": comparison_result
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi so sánh sản phẩm: {str(e)}"
            )
    
    def get_top_selling_products(self, db: Session, limit: int = 5) -> Response:
        """Lấy danh sách sản phẩm bán chạy nhất"""
        try:
            rag_handler = self.ai_integration.get_rag_handler()
            if not rag_handler:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.INTERNAL_SERVER_ERROR,
                    message="Không thể khởi tạo RAG Handler"
                )
            
            top_selling = rag_handler.get_top_selling_products(limit)
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="Lấy sản phẩm bán chạy thành công",
                data={
                    "top_selling_products": top_selling
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi lấy sản phẩm bán chạy: {str(e)}"
            )
    
    def get_top_liked_products(self, db: Session, limit: int = 5) -> Response:
        """Lấy danh sách sản phẩm được yêu thích nhất"""
        try:
            rag_handler = self.ai_integration.get_rag_handler()
            if not rag_handler:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.INTERNAL_SERVER_ERROR,
                    message="Không thể khởi tạo RAG Handler"
                )
            
            top_liked = rag_handler.get_top_liked_products(limit)
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="Lấy sản phẩm được yêu thích thành công",
                data={
                    "top_liked_products": top_liked
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi lấy sản phẩm được yêu thích: {str(e)}"
            )
    
    def get_least_selling_products(self, db: Session, limit: int = 5) -> Response:
        """Lấy danh sách sản phẩm bán ít nhất"""
        try:
            rag_handler = self.ai_integration.get_rag_handler()
            if not rag_handler:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.INTERNAL_SERVER_ERROR,
                    message="Không thể khởi tạo RAG Handler"
                )
            
            least_selling = rag_handler.get_least_selling_products(limit)
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="Lấy sản phẩm bán ít thành công",
                data={
                    "least_selling_products": least_selling
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi lấy sản phẩm bán ít: {str(e)}"
            )
    
    def verify_product(self, db: Session, product_identifier: str) -> Response:
        """Kiểm tra sản phẩm có tồn tại không"""
        try:
            rag_handler = self.ai_integration.get_rag_handler()
            if not rag_handler:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.INTERNAL_SERVER_ERROR,
                    message="Không thể khởi tạo RAG Handler"
                )
            
            exists = rag_handler.verify_product(product_identifier)
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="Kiểm tra sản phẩm thành công",
                data={
                    "exists": exists,
                    "product_identifier": product_identifier
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi kiểm tra sản phẩm: {str(e)}"
            )
