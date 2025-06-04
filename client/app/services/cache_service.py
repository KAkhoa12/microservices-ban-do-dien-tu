from django.core.cache import cache
from django.conf import settings
import hashlib
import json


def generate_cache_key(prefix, **kwargs):
    """Generate a unique cache key based on prefix and parameters"""
    # Sort kwargs to ensure consistent key generation
    sorted_kwargs = sorted(kwargs.items())
    key_data = f"{prefix}_{json.dumps(sorted_kwargs, sort_keys=True)}"
    # Use hash to keep key length manageable
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    return f"{prefix}_{key_hash}"


def get_cached_data(cache_key, fetch_function, timeout=None, *args, **kwargs):
    """
    Generic function to get data from cache or fetch from API
    
    Args:
        cache_key: Unique cache key
        fetch_function: Function to call if data not in cache
        timeout: Cache timeout in seconds
        *args, **kwargs: Arguments to pass to fetch_function
    """
    data = cache.get(cache_key)
    
    if data is None:
        try:
            data = fetch_function(*args, **kwargs)
            if timeout is None:
                timeout = getattr(settings, 'CACHE_TIMEOUTS', {}).get('default', 300)
            cache.set(cache_key, data, timeout)
        except Exception as e:
            print(f"Error fetching data for cache key {cache_key}: {e}")
            data = None
    
    return data


def invalidate_cache_pattern(pattern):
    """Invalidate all cache keys matching a pattern"""
    try:
        # This is a simple implementation - for production, consider using Redis with pattern matching
        cache.clear()  # For now, clear all cache
        print(f"Cache cleared for pattern: {pattern}")
    except Exception as e:
        print(f"Error clearing cache: {e}")


def get_cached_categories(category_id=None, **kwargs):
    """Get cached categories with optional filtering"""
    from .business_service import get_all_categories
    from ..views import safe_get_payload
    
    cache_key = generate_cache_key('categories', category_id=category_id, **kwargs)
    timeout = getattr(settings, 'CACHE_TIMEOUTS', {}).get('categories', 600)
    
    def fetch_categories():
        response = get_all_categories(category_id=category_id, **kwargs)
        return safe_get_payload(response)
    
    return get_cached_data(cache_key, fetch_categories, timeout)


def get_cached_brands(brand_id=None, **kwargs):
    """Get cached brands with optional filtering"""
    from .business_service import get_all_brands
    from ..views import safe_get_payload
    
    cache_key = generate_cache_key('brands', brand_id=brand_id, **kwargs)
    timeout = getattr(settings, 'CACHE_TIMEOUTS', {}).get('brands', 600)
    
    def fetch_brands():
        response = get_all_brands(brand_id=brand_id, **kwargs)
        return safe_get_payload(response)
    
    return get_cached_data(cache_key, fetch_brands, timeout)


def get_cached_products(category_id=None, brand_id=None, search=None, page=1, take=10, **kwargs):
    """Get cached products with optional filtering"""
    from .business_service import get_all_products, get_products_by_category, get_products_by_brand
    from ..views import safe_get_payload, safe_get_pagination
    
    cache_key = generate_cache_key(
        'products', 
        category_id=category_id, 
        brand_id=brand_id, 
        search=search, 
        page=page, 
        take=take, 
        **kwargs
    )
    timeout = getattr(settings, 'CACHE_TIMEOUTS', {}).get('products', 300)
    
    def fetch_products():
        if category_id:
            response = get_products_by_category(category_id, page=page, take=take)
        elif brand_id:
            response = get_products_by_brand(brand_id, page=page, take=take)
        else:
            response = get_all_products(search=search, page=page, take=take, **kwargs)
        
        return {
            'products': safe_get_payload(response),
            'pagination': safe_get_pagination(response)
        }
    
    return get_cached_data(cache_key, fetch_products, timeout)


def get_cached_product_by_id(product_id):
    """Get cached single product by ID"""
    from .business_service import get_product_by_id
    from ..views import safe_get_payload
    
    cache_key = f'product_{product_id}'
    timeout = getattr(settings, 'CACHE_TIMEOUTS', {}).get('products', 300)
    
    def fetch_product():
        response = get_product_by_id(product_id)
        products = safe_get_payload(response)
        return products[0] if products else {}
    
    return get_cached_data(cache_key, fetch_product, timeout)


def clear_product_cache():
    """Clear all product-related cache"""
    invalidate_cache_pattern('products')
    invalidate_cache_pattern('product_')


def clear_category_cache():
    """Clear all category-related cache"""
    invalidate_cache_pattern('categories')
    invalidate_cache_pattern('global_categories')


def get_cached_products(category_id=None, brand_id=None, search=None, page=1, take=10, **kwargs):
    """Get cached products with optional filtering"""
    from .business_service import get_all_products, get_products_by_category, get_products_by_brand
    from ..views import safe_get_payload, safe_get_pagination

    cache_key = generate_cache_key(
        'products',
        category_id=category_id,
        brand_id=brand_id,
        search=search,
        page=page,
        take=take,
        **kwargs
    )
    timeout = getattr(settings, 'CACHE_TIMEOUTS', {}).get('products', 300)

    def fetch_products():
        if category_id:
            response = get_products_by_category(category_id, page=page, take=take)
        elif brand_id:
            response = get_products_by_brand(brand_id, page=page, take=take)
        else:
            response = get_all_products(search=search, page=page, take=take, **kwargs)

        return {
            'products': safe_get_payload(response),
            'pagination': safe_get_pagination(response),
            'response': response
        }

    return get_cached_data(cache_key, fetch_products, timeout)


def clear_brand_cache():
    """Clear all brand-related cache"""
    invalidate_cache_pattern('brands')
