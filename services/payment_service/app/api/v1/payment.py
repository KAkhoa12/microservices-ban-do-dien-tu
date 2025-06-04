from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import json
import requests

from ...db.database import get_db
from ...schemas.payment import (
    PaymentCreateRequest, PaymentCreateResponse, 
    MomoCallbackRequest, MomoCallbackResponse,
    PaymentVerifyResponse, PaymentResponse
)
from ...utils.momo_service import create_momo_payment, verify_momo_response
from ...crud.payment import (
    get_payment_by_order_id, get_payments_by_user_id, 
    get_payment_by_id, update_payment_order_created
)
from ...core.config import settings

router = APIRouter()


@router.post("/create", response_model=PaymentCreateResponse)
async def create_payment(
    payment_request: PaymentCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Tạo thanh toán MoMo
    """
    try:
        result = create_momo_payment(
            db=db,
            amount=payment_request.amount,
            order_info=payment_request.order_info,
            user_id=payment_request.user_id,
            cart_data=payment_request.cart_data
        )
        
        return PaymentCreateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating payment: {str(e)}")


@router.get("/momo/result")
@router.post("/momo/result")
async def payment_result(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Xử lý kết quả thanh toán từ MoMo (return URL)
    """
    try:
        # Get data from request
        if request.method == "GET":
            data = dict(request.query_params)
        else:
            try:
                body = await request.body()
                data = json.loads(body)
            except:
                form_data = await request.form()
                data = dict(form_data)
        
        print("Received data from MoMo:", data)
        
        # Verify payment
        result = verify_momo_response(db, data)
        
        if result['status'] == 'verified':
            payment_data = result['payment']
            
            if payment_data['status'] == 'completed':
                # Create order in business service
                order_result = await create_order_from_payment(payment_data)
                
                if order_result.get('status') == 'success':
                    # Update payment with order ID
                    order_id = order_result.get('data', {}).get('id')
                    if order_id:
                        update_payment_order_created(db, payment_data['id'], order_id)
                
                return {
                    "status": "success",
                    "message": "Payment completed successfully",
                    "payment": payment_data,
                    "order": order_result.get('data', {})
                }
            else:
                return {
                    "status": "failed",
                    "message": "Payment failed",
                    "payment": payment_data
                }
        else:
            return {
                "status": "error",
                "message": result.get('message', 'Payment verification failed'),
                "debug": result.get('debug', {})
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing payment result: {str(e)}"
        }


@router.post("/momo/ipn", response_model=MomoCallbackResponse)
async def payment_ipn(
    callback_data: MomoCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    IPN (Instant Payment Notification) từ MoMo
    """
    try:
        data = callback_data.dict()
        
        # Verify payment
        result = verify_momo_response(db, data)
        
        if result['status'] == 'verified':
            return MomoCallbackResponse(
                partnerCode=data.get('partnerCode'),
                orderId=data.get('orderId'),
                requestId=data.get('requestId'),
                resultCode=0,
                message='Success'
            )
        else:
            return MomoCallbackResponse(
                partnerCode=data.get('partnerCode'),
                orderId=data.get('orderId'),
                requestId=data.get('requestId'),
                resultCode=1,
                message='Failed to verify'
            )
    except Exception as e:
        return MomoCallbackResponse(
            partnerCode=callback_data.partnerCode,
            orderId=callback_data.orderId,
            requestId=callback_data.requestId,
            resultCode=99,
            message=str(e)
        )


@router.get("/user/{user_id}", response_model=List[PaymentResponse])
async def get_user_payments(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách thanh toán của user
    """
    payments = get_payments_by_user_id(db, user_id, skip, limit)
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin thanh toán theo ID
    """
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


async def create_order_from_payment(payment_data: dict):
    """
    Tạo order từ thông tin payment thông qua business service
    """
    try:
        if not payment_data.get('cart_data'):
            return {"status": "error", "message": "No cart data found"}
        
        # Call business service to create order
        url = f"{settings.BUSINESS_SERVICE_URL}/api/order/create-order-from-cart"
        
        # Parse cart data
        cart_data = json.loads(payment_data['cart_data'])
        
        payload = {
            "user_id": payment_data['user_id'],
            "cart_data": cart_data,
            "payment_id": payment_data['id']
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error", 
                "message": f"Failed to create order: {response.text}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating order: {str(e)}"
        }
