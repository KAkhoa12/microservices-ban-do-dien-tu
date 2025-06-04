from typing import Optional
from sqlalchemy.orm import Session

from core.response import Response, StatusEnum, CodeEnum
from utils.aiagent_integration import AIAgentIntegration

class DataManagementCRUD:
    def __init__(self):
        self.ai_integration = AIAgentIntegration()
    
    def update_product_data(self, db: Session) -> Response:
        """Cập nhật dữ liệu sản phẩm từ database"""
        try:
            data_processor = self.ai_integration.get_data_processor()
            if not data_processor:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.INTERNAL_SERVER_ERROR,
                    message="Không thể khởi tạo DataProcessor"
                )
            
            result_message, product_count = data_processor.generate_product_data()
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="Cập nhật dữ liệu sản phẩm thành công",
                data={
                    "message": result_message,
                    "product_count": product_count,
                    "last_update": data_processor.get_last_update_time()
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi cập nhật dữ liệu sản phẩm: {str(e)}"
            )
    
    def update_custom_data(self, db: Session, custom_data: str) -> Response:
        """Cập nhật dữ liệu tùy chỉnh"""
        try:
            data_processor = self.ai_integration.get_data_processor()
            if not data_processor:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.INTERNAL_SERVER_ERROR,
                    message="Không thể khởi tạo DataProcessor"
                )
            
            result_message = data_processor.save_custom_data(custom_data)
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="Cập nhật dữ liệu tùy chỉnh thành công",
                data={
                    "message": result_message
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi cập nhật dữ liệu tùy chỉnh: {str(e)}"
            )
    
    def get_custom_data(self, db: Session) -> Response:
        """Lấy dữ liệu tùy chỉnh hiện tại"""
        try:
            data_processor = self.ai_integration.get_data_processor()
            if not data_processor:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.INTERNAL_SERVER_ERROR,
                    message="Không thể khởi tạo DataProcessor"
                )
            
            custom_data = data_processor.get_custom_data()
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="Lấy dữ liệu tùy chỉnh thành công",
                data={
                    "custom_data": custom_data,
                    "last_update": data_processor.get_last_update_time()
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi lấy dữ liệu tùy chỉnh: {str(e)}"
            )
    
    def update_vector_database(self, db: Session) -> Response:
        """Cập nhật vector database"""
        try:
            result_message = self.ai_integration.update_vectordb()
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="Cập nhật vector database thành công",
                data={
                    "message": result_message
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi cập nhật vector database: {str(e)}"
            )
    
    def get_data_status(self, db: Session) -> Response:
        """Lấy trạng thái dữ liệu hiện tại"""
        try:
            data_processor = self.ai_integration.get_data_processor()
            if not data_processor:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.INTERNAL_SERVER_ERROR,
                    message="Không thể khởi tạo DataProcessor"
                )
            
            product_count = data_processor.get_product_count()
            last_update = data_processor.get_last_update_time()
            custom_data = data_processor.get_custom_data()
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="Lấy trạng thái dữ liệu thành công",
                data={
                    "product_count": product_count,
                    "last_update": last_update,
                    "has_custom_data": bool(custom_data.strip()) if custom_data else False,
                    "custom_data_length": len(custom_data) if custom_data else 0
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi lấy trạng thái dữ liệu: {str(e)}"
            )
