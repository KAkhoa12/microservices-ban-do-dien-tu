import requests
from ..routes import UserRoutes
from .base import API_URL, handle_response

def get_user_info(user_id: int):
    """Get user information by user ID (legacy method)"""
    url = f"{API_URL}{UserRoutes.ME.value}"
    response = requests.get(url, headers={"user_id": str(user_id)})
    return handle_response(response)

def get_current_user(token: str):
    url = f"{API_URL}{UserRoutes.ME.value}"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    return handle_response(response)

def update_user_info(user_id: int, data: dict, token: str = None):
    """Update user information"""
    url = f"{API_URL}{UserRoutes.UPDATE_INFO.value}"

    # Add user_id to data as required by UserUpdate schema
    data['id'] = user_id

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.put(url, json=data, headers=headers)
    return handle_response(response)

def update_user_avatar(user_id: int, image_file, token: str = None):
    """Update user avatar"""
    url = f"{API_URL}{UserRoutes.UPDATE_AVATAR.value}"
    files = {"image": image_file}
    data = {"user_id": user_id}

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.put(url, files=files, data=data, headers=headers)
    return handle_response(response)

def login_user(username: str, password: str):
    """Login user"""
    url = f"{API_URL}{UserRoutes.LOGIN.value}"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    return handle_response(response)

def register_user(username: str, email: str, password: str, full_name: str):
    """Register user"""
    url = f"{API_URL}{UserRoutes.REGISTER.value}"
    data = {"username": username, "email": email, "password": password, "full_name": full_name}
    response = requests.post(url, json=data)
    return handle_response(response)

def validate_user(token: str):
    """Validate user token"""
    url = f"{API_URL}{UserRoutes.VALIDATE.value}"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    return handle_response(response)

def validate_admin(token: str):
    """Validate admin token"""
    url = f"{API_URL}{UserRoutes.ADMIN_VALIDATE.value}"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    return handle_response(response)

# ==================== ADMIN USER MANAGEMENT APIs ====================

def get_all_users(token: str = None, skip: int = 0, limit: int = 100, take: int = 10):
    """Get all users for admin"""
    url = f"{API_URL}{UserRoutes.ADMIN_LIST_USER.value}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(url, headers=headers, params={"skip": skip, "limit": limit, "take": take})
    return handle_response(response)

def get_user_by_id(user_id: int, token: str = None):
    """Get user by ID for admin"""
    url = f"{API_URL}{UserRoutes.ME.value}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    headers["user_id"] = str(user_id)
    response = requests.get(url, headers=headers)
    return handle_response(response)

def create_user(user_data: dict, token: str = None):
    """Create new user (admin only)"""
    url = f"{API_URL}{UserRoutes.REGISTER.value}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.post(url, json=user_data, headers=headers)
    return handle_response(response)

def update_user_by_admin(user_id: int, user_data: dict, token: str = None):
    """Update user information by admin"""
    url = f"{API_URL}{UserRoutes.UPDATE_INFO.value}"
    headers = {"user_id": str(user_id)}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.put(url, json=user_data, headers=headers)
    return handle_response(response)

def delete_user(user_id: int, token: str = None):
    """Delete user by admin"""
    url = f"{API_URL}{UserRoutes.ADMIN_DELETE_USER.value}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.delete(url, headers=headers, params={"user_id": user_id})
    return handle_response(response)
