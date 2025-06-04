import os
import sys
import importlib.util
from pathlib import Path

class AIAgentIntegration:
    """
    Class để tích hợp với các module AI Agent từ frontend
    """
    
    def __init__(self):
        self.base_dir = self._get_base_dir()
        self.frontend_aiagent_path = os.path.join(self.base_dir, 'DoAn_QuanLyDoDienTu', 'frontend', 'aiagent')
        self._add_frontend_to_path()
        
    def _get_base_dir(self):
        """Lấy đường dẫn gốc của project"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Đi lên 4 cấp từ utils -> app -> chatbot_service -> services -> root
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
    
    def _add_frontend_to_path(self):
        """Thêm đường dẫn frontend vào sys.path để import được các module"""
        if self.frontend_aiagent_path not in sys.path:
            sys.path.insert(0, self.frontend_aiagent_path)
            
        # Thêm đường dẫn frontend root
        frontend_root = os.path.join(self.base_dir, 'DoAn_QuanLyDoDienTu')
        if frontend_root not in sys.path:
            sys.path.insert(0, frontend_root)
    
    def get_data_processor(self):
        """Lấy instance của DataProcessor từ frontend"""
        try:
            from data_processor import DataProcessor
            return DataProcessor()
        except ImportError as e:
            print(f"Không thể import DataProcessor: {e}")
            return None
    
    def get_rag_handler(self, api_key=None, model=None, debug=False):
        """Lấy instance của RAGHandler từ frontend"""
        try:
            from rag_handler import RAGHandler
            return RAGHandler(api_key=api_key, model=model, debug=debug)
        except ImportError as e:
            print(f"Không thể import RAGHandler: {e}")
            return None
    
    def update_vectordb(self):
        """Cập nhật vector database sử dụng module từ frontend"""
        try:
            from update_vectordb import update_vectordb
            return update_vectordb()
        except ImportError as e:
            print(f"Không thể import update_vectordb: {e}")
            return f"Lỗi import: {e}"
