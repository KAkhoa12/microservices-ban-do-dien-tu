import requests
from ..routes import CartRoutes
from .base import API_URL, handle_response

def get_cart(user_id: int):
    """Get user's cart items"""
    url = f"{API_URL}{CartRoutes.GET_CART.value}"
    response = requests.get(url, params={"user_id": user_id})
    return handle_response(response)

def add_to_cart(user_id: int, product_id: int, quantity: int = 1):
    """Add item to cart"""
    url = f"{API_URL}{CartRoutes.ADD_TO_CART.value}"
    params = {"user_id": user_id}
    data = {
        "product_id": product_id,
        "quantity": quantity
    }
    response = requests.post(url, params=params, json=data)
    return handle_response(response)

def update_cart_item(user_id: int, product_id: int, quantity: int):
    """Update cart item quantity"""
    url = f"{API_URL}{CartRoutes.UPDATE_CART_ITEM.value}"
    params = {
        "user_id": user_id,
        "product_id": product_id,
        "quantity": quantity
    }
    response = requests.put(url, params=params)
    return handle_response(response)

def remove_from_cart(user_id: int, product_id: int):
    """Remove item from cart"""
    url = f"{API_URL}{CartRoutes.REMOVE_FROM_CART.value}"
    response = requests.delete(url, params={
        "user_id": user_id,
        "product_id": product_id
    })
    return handle_response(response)

def clear_cart(user_id: int):
    """Clear all items from cart"""
    url = f"{API_URL}{CartRoutes.CLEAR_CART.value}"
    response = requests.delete(url, params={"user_id": user_id})
    return handle_response(response)
