from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: int

class ChatMessage(BaseModel):
    id: int
    session_id: str
    message_type: str
    content: str
    created_at: datetime
    metadata: Optional[str] = None

class ChatSession(BaseModel):
    id: int
    session_id: str
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    metadata: Optional[str] = None

class ChatHistory(BaseModel):
    session: ChatSession
    messages: List[ChatMessage]

class ProductInfoRequest(BaseModel):
    product_identifier: str

class CompareProductsRequest(BaseModel):
    product1_identifier: str
    product2_identifier: str

class TopProductsRequest(BaseModel):
    limit: Optional[int] = 5

class UpdateDataRequest(BaseModel):
    custom_data: Optional[str] = None
    force_update: Optional[bool] = False
