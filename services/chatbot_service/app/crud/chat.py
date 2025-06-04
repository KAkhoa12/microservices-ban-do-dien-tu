import uuid
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.chat_session import ChatSession
from models.chat_message import ChatMessage
from schemas.chat import ChatRequest, ChatResponse, ChatHistory
from core.response import Response, StatusEnum, CodeEnum
from utils.aiagent_integration import AIAgentIntegration

class ChatCRUD:
    def __init__(self):
        self.ai_integration = AIAgentIntegration()
        
    def create_session(self, db: Session, user_id: Optional[int] = None) -> str:
        """Tạo session chat mới"""
        session_id = str(uuid.uuid4())
        
        db_session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            is_active=True
        )
        
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        return session_id
    
    def get_session(self, db: Session, session_id: str) -> Optional[ChatSession]:
        """Lấy thông tin session"""
        return db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.is_active == True
        ).first()
    
    def save_message(self, db: Session, session_id: str, message_type: str, content: str, metadata: Optional[dict] = None) -> ChatMessage:
        """Lưu tin nhắn vào database"""
        db_message = ChatMessage(
            session_id=session_id,
            message_type=message_type,
            content=content,
            metadata=json.dumps(metadata) if metadata else None
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        return db_message
    
    def get_chat_history(self, db: Session, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Lấy lịch sử chat của session"""
        return db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(desc(ChatMessage.created_at)).limit(limit).all()
    
    def process_chat(self, db: Session, chat_request: ChatRequest) -> Response:
        """Xử lý tin nhắn chat"""
        try:
            # Tạo session mới nếu chưa có
            if not chat_request.session_id:
                session_id = self.create_session(db, chat_request.user_id)
            else:
                session_id = chat_request.session_id
                # Kiểm tra session có tồn tại không
                session = self.get_session(db, session_id)
                if not session:
                    session_id = self.create_session(db, chat_request.user_id)
            
            # Lưu tin nhắn của user
            user_message = self.save_message(
                db, session_id, "user", chat_request.message
            )
            
            # Xử lý với AI Agent
            rag_handler = self.ai_integration.get_rag_handler(debug=True)
            if not rag_handler:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.INTERNAL_SERVER_ERROR,
                    message="Không thể khởi tạo AI Agent"
                )
            
            # Gọi function calling để xử lý
            ai_response = rag_handler.function_calling(chat_request.message)
            
            # Trích xuất nội dung từ response
            clean_response = rag_handler.extract_content(ai_response)
            
            # Lưu phản hồi của AI
            ai_message = self.save_message(
                db, session_id, "assistant", clean_response
            )
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="Chat processed successfully",
                data={
                    "response": clean_response,
                    "session_id": session_id,
                    "message_id": ai_message.id
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi xử lý chat: {str(e)}"
            )
    
    def get_session_history(self, db: Session, session_id: str) -> Response:
        """Lấy lịch sử chat của session"""
        try:
            session = self.get_session(db, session_id)
            if not session:
                return Response(
                    status=StatusEnum.ERROR,
                    code=CodeEnum.NOT_FOUND,
                    message="Session không tồn tại"
                )
            
            messages = self.get_chat_history(db, session_id)
            
            return Response(
                status=StatusEnum.SUCCESS,
                code=CodeEnum.SUCCESS,
                message="Lấy lịch sử chat thành công",
                data={
                    "session": {
                        "id": session.id,
                        "session_id": session.session_id,
                        "user_id": session.user_id,
                        "created_at": session.created_at,
                        "is_active": session.is_active
                    },
                    "messages": [
                        {
                            "id": msg.id,
                            "message_type": msg.message_type,
                            "content": msg.content,
                            "created_at": msg.created_at,
                            "metadata": json.loads(msg.metadata) if msg.metadata else None
                        }
                        for msg in reversed(messages)  # Đảo ngược để hiển thị theo thứ tự thời gian
                    ]
                }
            )
            
        except Exception as e:
            return Response(
                status=StatusEnum.ERROR,
                code=CodeEnum.INTERNAL_SERVER_ERROR,
                message=f"Lỗi lấy lịch sử chat: {str(e)}"
            )
