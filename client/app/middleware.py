from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import json

class TokenAuthMiddleware(MiddlewareMixin):
    """
    Middleware to handle JWT token authentication
    Checks for token in cookies, headers, or request body
    """
    
    def process_request(self, request):
        # Initialize user data
        request.user_data = None
        request.is_authenticated = False
        request.is_admin = False
        
        # Get token from various sources
        token = self.get_token_from_request(request)
        
        if token:
            user_data = self.validate_token(token)
            if user_data:
                request.user_data = user_data
                request.is_authenticated = True
                request.is_admin = user_data.get('user_role') == 'admin'

                # Không lưu session nữa, chỉ set request attributes
        else:
            # No valid token
            request.user_data = None
            request.is_authenticated = False
            request.is_admin = False
    
    def get_token_from_request(self, request):
        """Extract JWT token from request (supports both cookies and localStorage)"""
        # 1. Try Authorization header (recommended for localStorage)
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]

        # 2. Try cookies (for traditional cookie-based auth)
        token = request.COOKIES.get('access_token')
        if token:
            return token

        # 3. Try custom header (alternative for localStorage)
        token = request.META.get('HTTP_X_ACCESS_TOKEN', '')
        if token:
            return token

        # 4. Try request body for POST requests (for localStorage via AJAX)
        if request.method == 'POST' and hasattr(request, 'body'):
            try:
                body = json.loads(request.body)
                token = body.get('access_token')
                if token:
                    return token
            except:
                pass

        # 5. Try GET parameters (for localStorage via URL)
        token = request.GET.get('access_token')
        if token:
            return token

        return None
    
    def validate_token(self, token):
        """Validate JWT token by calling user service"""
        if not token:
            return None
        
        try:
            from .services.user_service import get_current_user
            response = get_current_user(token)
            
            if response.get('status') == 'success':
                return response.get('data')
            return None
        except Exception as e:
            print(f"Token validation error: {e}")
            return None

