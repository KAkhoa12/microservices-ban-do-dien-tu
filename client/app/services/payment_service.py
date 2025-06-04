import requests
import json
from .base import API_URL, handle_response


def create_payment(amount: int, order_info: str, user_id: int, cart_data: dict = None):
    """
    Tạo thanh toán thông qua Payment Service
    """
    url = f"{API_URL}/api/payment/create"
    
    payload = {
        "amount": amount,
        "order_info": order_info,
        "user_id": user_id,
        "cart_data": json.dumps(cart_data) if cart_data else None
    }
    
    try:
        response = requests.post(url, json=payload)
        return handle_response(response)
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error calling payment service: {str(e)}'
        }


def get_user_payments(user_id: int, skip: int = 0, limit: int = 100):
    """
    Lấy danh sách thanh toán của user
    """
    url = f"{API_URL}/api/payment/user/{user_id}"
    params = {"skip": skip, "limit": limit}
    
    try:
        response = requests.get(url, params=params)
        return handle_response(response)
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error getting user payments: {str(e)}'
        }


def get_payment_by_id(payment_id: int):
    """
    Lấy thông tin thanh toán theo ID
    """
    url = f"{API_URL}/api/payment/{payment_id}"
    
    try:
        response = requests.get(url)
        return handle_response(response)
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error getting payment: {str(e)}'
        }
