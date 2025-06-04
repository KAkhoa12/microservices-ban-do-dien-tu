import requests
from ..routes import OrderRoutes
from .base import API_URL, handle_response

def get_orders(page: int = 1, take: int = 10, user_id: int = None, status: str = None, order_id: int = None, search: str = None):
    """Get orders with pagination and filtering"""
    url = f"{API_URL}{OrderRoutes.ORDERS.value}"
    params = {"page": page, "take": take}
    if user_id:
        params["user_id"] = user_id
    if status:
        params["status"] = status
    if order_id:
        params["order_id"] = order_id
    if search:
        params["search"] = search
    response = requests.get(url, params=params)
    return handle_response(response)

def get_order(order_id: int):
    """Get single order by ID"""
    url = f"{API_URL}{OrderRoutes.GET_ORDER.value}"
    response = requests.get(url, params={"order_id": order_id})
    return handle_response(response)

def create_order(user_id: int, total_price: float, order_details: list, status: str = "pending"):
    """Create new order"""
    url = f"{API_URL}{OrderRoutes.CREATE_ORDER.value}"
    data = {
        "user_id": user_id,
        "total_price": total_price,
        "status": status,
        "order_details": order_details
    }
    response = requests.post(url, json=data)
    return handle_response(response)

def create_order_from_cart(user_id: int):
    """Create order from user's cart"""
    url = f"{API_URL}{OrderRoutes.CREATE_ORDER_FROM_CART.value}"
    response = requests.post(url, params={"user_id": user_id})
    return handle_response(response)

def update_order(order_id: int, total_price: float = None, status: str = None):
    """Update order"""
    url = f"{API_URL}{OrderRoutes.UPDATE_ORDER.value}"
    data = {"order_id": order_id}
    if total_price is not None:
        data["total_price"] = total_price
    if status is not None:
        data["status"] = status
    response = requests.put(url, json=data)
    return handle_response(response)

def update_order_status(order_id: int, status: str):
    """Update order status"""
    url = f"{API_URL}{OrderRoutes.UPDATE_ORDER_STATUS.value}"
    data = {
        "order_id": order_id,
        "status": status
    }
    response = requests.put(url, json=data)
    return handle_response(response)

def cancel_order(order_id: int):
    """Cancel order and restore stock"""
    url = f"{API_URL}{OrderRoutes.CANCEL_ORDER.value}"
    response = requests.put(url, params={"order_id": order_id})
    return handle_response(response)

def delete_order(order_id: int):
    """Delete order (admin only)"""
    url = f"{API_URL}{OrderRoutes.DELETE_ORDER.value}"
    response = requests.delete(url, params={"order_id": order_id})
    return handle_response(response)
