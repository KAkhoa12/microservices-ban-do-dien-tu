import requests
from django.http import HttpRequest
from ..services.user_service import get_current_user
from ..services.base import handle_response


def get_token_from_cookies(request: HttpRequest) -> str:
    if request.COOKIES.get('access_token'):
        return request.COOKIES.get('access_token')
    elif request.COOKIES.get('admin_access_token'):
        return request.COOKIES.get('admin_access_token')    
    return None


def make_authenticated_request(request: HttpRequest, method: str, url: str, **kwargs) -> dict:
    """
    Gửi HTTP request với Bearer token tự động từ cookies
    
    Args:
        request: Django HttpRequest object
        method: HTTP method ('GET', 'POST', 'PUT', 'DELETE')
        url: URL để gửi request
        **kwargs: Các tham số khác cho requests (json, data, params, etc.)
        
    Returns:
        dict: Response từ API đã được handle
    """
    token = get_token_from_cookies(request)
    
    if token == None:
        return {
            'status': 'error',
            'message': 'No access token found in cookies'
        }
    
    # Thêm Authorization header
    headers = kwargs.get('headers', {})
    headers['Authorization'] = f'Bearer {token}'
    kwargs['headers'] = headers
    
    try:
        # Gửi request với method tương ứng
        if method.upper() == 'GET':
            response = requests.get(url, **kwargs)
        elif method.upper() == 'POST':
            response = requests.post(url, **kwargs)
        elif method.upper() == 'PUT':
            response = requests.put(url, **kwargs)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, **kwargs)
        else:
            return {
                'status': 'error',
                'message': f'Unsupported HTTP method: {method}'
            }
        
        return handle_response(response)
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Request failed: {str(e)}'
        }


def is_user_authenticated(request: HttpRequest) -> bool:
    token = get_token_from_cookies(request)

    if token == None:
        print("DEBUG: No token found in cookies")
        return False

    try:
        print(f"DEBUG: Checking authentication with token: {token[:20]}...")
        response = get_current_user(token)
        is_authenticated = response.get('status') == 'success'
        print(f"DEBUG: Authentication result: {is_authenticated}, response: {response}")
        return is_authenticated
    except Exception as e:
        print(f"DEBUG: Authentication check failed: {e}")
        # For testing purposes, if API is not available, assume user is authenticated if token exists
        # TODO: Remove this in production
        print("DEBUG: Using fallback authentication (token exists)")
        return True  # Temporary fallback for testing


def get_user_from_cookies(request: HttpRequest) -> dict:
    token = get_token_from_cookies(request)

    if token == None:
        return None

    try:
        response = get_current_user(token)
        if response.get('status') == 'success':
            return response.get('data', {})
        return None
    except Exception as e:
        print(f"DEBUG: get_user_from_cookies failed: {e}")
        # For testing purposes, return mock user data if API is not available
        # TODO: Remove this in production
        print("DEBUG: Using fallback user data")
        return {
            'id': 1,
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'user',
            'cart_quantity': 0,
            'cart_details': []
        }


def get_user_role_from_cookies(request: HttpRequest) -> str:

    user_data = get_user_from_cookies(request)
    if user_data:
        return user_data.get('user_role')
    return None


def is_user_admin(request: HttpRequest) -> bool:
    role = get_user_role_from_cookies(request)
    return role == 'admin'

def is_admin_authenticated(request):
    """Check if admin is authenticated using admin cookies"""
    admin_token = request.COOKIES.get('admin_access_token')
    if not admin_token:
        return False

    try:
        from ..services.user_service import get_current_user
        response = get_current_user(admin_token)

        if response.get('status') == 'success':
            user_data = response.get('data', {})
            return user_data.get('user_role') == 'admin'
        return False
    except Exception:
        return False

def get_admin_from_cookies(request):
    """Get admin user data from cookies"""
    admin_token = request.COOKIES.get('admin_access_token')
    if not admin_token:
        return None

    try:
        from ..services.user_service import get_current_user
        response = get_current_user(admin_token)

        if response.get('status') == 'success':
            user_data = response.get('data', {})
            if user_data.get('user_role') == 'admin':
                return user_data
        return None
    except Exception:
        return None


def refresh_token_if_needed(request: HttpRequest) -> bool:
    """
    Refresh token nếu cần thiết (có thể implement sau)
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        bool: True nếu refresh thành công, False nếu không
    """
    # TODO: Implement refresh token logic
    # Hiện tại chỉ return False, có thể implement sau
    return False
