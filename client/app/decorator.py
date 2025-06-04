from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages
from django.http import JsonResponse
from .services.user_service import validate_user, validate_admin
from .utils.auth_utils import (
    get_token_from_cookies,
    is_user_authenticated,
    get_user_from_cookies,
    is_user_admin
)
import json

def get_token_from_request(request):
    """Extract JWT token from request (supports both cookies and localStorage)"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]

    # 2. Try cookies (for traditional cookie-based auth)
    token = request.COOKIES.get('access_token')
    if token:
        return token

    # 3. Try request body for POST requests (for localStorage via AJAX)
    if request.method == 'POST' and hasattr(request, 'body'):
        try:
            body = json.loads(request.body)
            token = body.get('access_token')
            if token:
                return token
        except:
            pass

    # 4. Try GET parameters (for localStorage via URL)
    token = request.GET.get('access_token')
    if token:
        return token

    return None

def login_required_api(view_func):
    """Decorator to require authentication using API validation"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Get token from request
        token = get_token_from_request(request)

        if not token:
            # Check for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Authentication required',
                    'redirect': '/login/'
                }, status=401)

            messages.error(request, 'Bạn cần đăng nhập để truy cập trang này.')
            return redirect('login')

        # Validate token using API
        try:
            validation_response = validate_user(token)

            # Check if validation was successful based on status
            if validation_response.get('status') != 'success':
                # Check for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid or expired token',
                        'redirect': '/login/'
                    }, status=401)

                messages.error(request, 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.')
                return redirect('login')

        except Exception as e:
            # Handle API call errors
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Authentication service unavailable',
                    'redirect': '/login/'
                }, status=503)

            messages.error(request, 'Lỗi xác thực. Vui lòng thử lại.')
            return redirect('login')

        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required_api(view_func):
    """Decorator to require admin role using API validation"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Get token from request
        token = get_token_from_request(request)

        if not token:
            # Check for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Authentication required',
                    'redirect': '/login/'
                }, status=401)

            messages.error(request, 'Bạn cần đăng nhập để truy cập trang này.')
            return redirect('login')

        # Validate admin token using API
        try:
            validation_response = validate_admin(token)

            # Check if validation was successful based on status
            if validation_response.get('status') != 'success':
                # Check for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Admin access required or invalid token',
                        'redirect': '/login/'
                    }, status=403)

                messages.error(request, 'Bạn không có quyền truy cập trang này hoặc phiên đăng nhập đã hết hạn.')
                return redirect('home')

        except Exception:
            # Handle API call errors
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Authentication service unavailable',
                    'redirect': '/login/'
                }, status=503)

            messages.error(request, 'Lỗi xác thực. Vui lòng thử lại.')
            return redirect('login')

        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Legacy decorators for backward compatibility (using middleware)
def login_required(view_func):
    """Decorator to require authentication (token or session) - Legacy version using middleware"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is authenticated via middleware
        if not getattr(request, 'is_authenticated', False):
            # Check for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Authentication required',
                    'redirect': '/login/'
                }, status=401)

            messages.error(request, 'Bạn cần đăng nhập để truy cập trang này.')
            return redirect('login')

        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    """Decorator to require admin role - Legacy version using middleware"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is authenticated
        if not getattr(request, 'is_authenticated', False):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Authentication required',
                    'redirect': '/login/'
                }, status=401)

            messages.error(request, 'Bạn cần đăng nhập để truy cập trang này.')
            return redirect('login')

        # Check if user is admin
        if not getattr(request, 'is_admin', False):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Admin access required'
                }, status=403)

            messages.error(request, 'Bạn không có quyền truy cập trang này.')
            return redirect('home')

        return view_func(request, *args, **kwargs)
    return _wrapped_view

def session_admin_required(view_func):
    """Legacy decorator for session-based admin check (backward compatibility)"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.path.startswith('/dashboard/'):
            if not request.session.get('role') == 'admin':
                return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_cookie_required(view_func):
    """Decorator to require admin authentication using cookies"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from .utils.auth_utils import is_admin_authenticated

        if not is_admin_authenticated(request):
            return redirect('dashboard_login')

        return view_func(request, *args, **kwargs)
    return _wrapped_view