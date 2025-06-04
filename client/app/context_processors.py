
from django.core.cache import cache
from django.conf import settings


def get_cached_categories():
    """Get categories from cache or API if not cached"""
    cache_key = 'global_categories'
    categories = cache.get(cache_key)

    if categories is None:
        try:
            # Import here to avoid circular imports
            from .services.business_service import get_all_categories
            from .views import safe_get_payload

            categories_response = get_all_categories()
            categories = safe_get_payload(categories_response)

            # Cache for the configured timeout
            timeout = getattr(settings, 'CACHE_TIMEOUTS', {}).get('categories', 600)
            cache.set(cache_key, categories, timeout)
        except Exception as e:
            print(f"Error fetching categories: {e}")
            categories = []

    return categories


def global_context(request):
    """Global context processor for common data like categories"""
    return {
        'global_categories': get_cached_categories(),
    }


def auth_context(request):
    try:
        # Import here to avoid circular imports
        from .utils.auth_utils import (
            is_user_authenticated,
            get_user_from_cookies,
            is_user_admin
        )

        # Get user authentication status and data using API
        user_authenticated = is_user_authenticated(request)
        current_user = get_user_from_cookies(request) if user_authenticated else None
        user_is_admin = is_user_admin(request) if user_authenticated else False

        return {
            'user_authenticated': user_authenticated,
            'user_is_admin': user_is_admin,
            'current_user': current_user,
            # Backward compatibility - add user data to session-like context
            'user_session': {
                'user_id': current_user.get('id') if current_user else None,
                'name': current_user.get('full_name') if current_user else None,
                'role': current_user.get('user_role') if current_user else None,
                'email': current_user.get('email') if current_user else None,

            }
        }
    except Exception as e:
        # If there's any error, return empty context
        print(f"Auth context processor error: {e}")
        return {
            'user_authenticated': False,
            'user_is_admin': False,
            'current_user': None,
            'user_session': {
                'user_id': None,
                'name': None,
                'role': None,
                'email': None,
            }
        }
