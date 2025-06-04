from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class PaymentCreateRequest(BaseModel):
    amount: int
    order_info: str
    user_id: int
    cart_data: Optional[str] = None


class PaymentCreateResponse(BaseModel):
    status: str
    message: Optional[str] = None
    payment_url: Optional[str] = None
    order_id: Optional[str] = None
    request_id: Optional[str] = None


class MomoCallbackRequest(BaseModel):
    partnerCode: str
    orderId: str
    requestId: str
    amount: str
    responseTime: str
    message: str
    resultCode: str
    signature: str
    transId: Optional[str] = None
    orderInfo: Optional[str] = None
    orderType: Optional[str] = None
    extraData: Optional[str] = None
    payType: Optional[str] = None


class MomoCallbackResponse(BaseModel):
    partnerCode: str
    orderId: str
    requestId: str
    resultCode: int
    message: str


class PaymentVerifyResponse(BaseModel):
    status: str
    message: Optional[str] = None
    payment: Optional[dict] = None
    debug: Optional[dict] = None


class PaymentBase(BaseModel):
    order_id: str
    amount: Decimal
    order_info: str
    request_id: str
    status: str


class PaymentResponse(PaymentBase):
    id: int
    transaction_id: Optional[str] = None
    message: Optional[str] = None
    response_time: Optional[datetime] = None
    user_id: Optional[int] = None
    order_created: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
