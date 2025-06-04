import requests
from ..routes import BrandRoutes, CategoryRoutes, ProductRoutes
from .base import API_URL, handle_response

# ==================== BRAND APIs ====================

def get_all_brands(page: int = 1, take: int = 10, name: str = None, slug: str = None, search: str = None, brand_id: int = None):
    """Get all brands with pagination using page number"""
    url = f"{API_URL}{BrandRoutes.BRANDS.value}"
    params = {"page": page, "take": take}
    if name:
        params["name"] = name
    if slug:
        params["slug"] = slug
    if search:
        params["search"] = search
    if brand_id:
        params["brand_id"] = brand_id
    response = requests.get(url, params=params)
    return handle_response(response)

def get_brand_by_id(brand_id: int):
    """Get brand by ID"""
    url = f"{API_URL}{BrandRoutes.BRANDS.value}"
    params = {"brand_id": brand_id}
    response = requests.get(url, params=params)
    return handle_response(response)

def create_brand(brand_data: dict):
    """Create new brand"""
    url = f"{API_URL}{BrandRoutes.CREATE_BRAND.value}"
    response = requests.post(url, json=brand_data)
    return handle_response(response)

def update_brand_info(brand_id: int, brand_data: dict):
    """Update brand information"""
    url = f"{API_URL}{BrandRoutes.UPDATE_INFO.value}"
    data = {"brand_id": brand_id, **brand_data}
    response = requests.put(url, json=data)
    return handle_response(response)

def update_brand_avatar(brand_id: int, avatar_data: dict):
    """Update brand avatar/logo"""
    url = f"{API_URL}{BrandRoutes.UPDATE_AVATAR.value}"
    data = {"brand_id": brand_id, **avatar_data}
    response = requests.put(url, json=data)
    return handle_response(response)

def delete_brand(brand_id: int):
    """Delete brand"""
    url = f"{API_URL}{BrandRoutes.DELETE_BRAND.value}"
    data = {"brand_id": brand_id}
    response = requests.delete(url, json=data)
    return handle_response(response)

# ==================== CATEGORY APIs ====================

def get_all_categories(page: int = 1, take: int = 10, name: str = None, slug: str = None, search: str = None, category_id: int = None):
    """Get all categories with pagination using page number"""
    url = f"{API_URL}{CategoryRoutes.CATEGORIES.value}"
    params = {"page": page, "take": take}
    if name:
        params["name"] = name
    if slug:
        params["slug"] = slug
    if search:
        params["search"] = search
    if category_id:
        params["category_id"] = category_id
    response = requests.get(url, params=params)
    return handle_response(response)

def get_category_by_id(category_id: int):
    """Get category by ID"""
    url = f"{API_URL}{CategoryRoutes.CATEGORIES.value}"
    params = {"category_id": category_id}
    response = requests.get(url, params=params)
    return handle_response(response)

def create_category(category_data: dict):
    """Create new category"""
    url = f"{API_URL}{CategoryRoutes.CREATE_CATEGORY.value}"
    response = requests.post(url, json=category_data)
    return handle_response(response)

def update_category_info(category_id: int, category_data: dict):
    """Update category information"""
    url = f"{API_URL}{CategoryRoutes.UPDATE_CATEGORY.value}"
    data = {"category_id": category_id, **category_data}
    response = requests.put(url, json=data)
    return handle_response(response)

def update_category_image(category_id: int, image_data: dict):
    """Update category image"""
    url = f"{API_URL}{CategoryRoutes.UPDATE_CATEGORY_IMAGE.value}"
    data = {"category_id": category_id, **image_data}
    response = requests.put(url, json=data)
    return handle_response(response)

def delete_category(category_id: int):
    """Delete category"""
    url = f"{API_URL}{CategoryRoutes.DELETE_CATEGORY.value}"
    data = {"category_id": category_id}
    response = requests.delete(url, json=data)
    return handle_response(response)

# ==================== PRODUCT APIs ====================

def get_all_products(page: int = 1, take: int = 10, name: str = None, search: str = None, category_id: int = None, brand_id: int = None):
    """Get all products with pagination using page number"""
    url = f"{API_URL}{ProductRoutes.PRODUCTS.value}"
    params = {"page": page, "take": take}
    if name:
        params["name"] = name
    if search:
        params["search"] = search
    if category_id:
        params["category_id"] = category_id
    if brand_id:
        params["brand_id"] = brand_id
    response = requests.get(url, params=params)
    return handle_response(response)

def get_product_by_id(product_id: int):
    """Get product by ID"""
    url = f"{API_URL}{ProductRoutes.PRODUCTS.value}"
    response = requests.get(url, params={"product_id": product_id, "take": 1})
    return handle_response(response)

def create_product(product_data: dict):
    """Create new product"""
    url = f"{API_URL}{ProductRoutes.CREATE_PRODUCT.value}"
    response = requests.post(url, json=product_data)
    return handle_response(response)

def update_product_info(product_id: int, product_data: dict):
    """Update product information"""
    url = f"{API_URL}{ProductRoutes.UPDATE_PRODUCT.value}"
    data = {"product_id": product_id, **product_data}
    response = requests.put(url, json=data)
    return handle_response(response)

def update_product_image(product_id: int, image_data: dict):
    """Update product image"""
    url = f"{API_URL}{ProductRoutes.UPDATE_PRODUCT_IMAGE.value}"
    data = {"product_id": product_id, **image_data}
    response = requests.put(url, json=data)
    return handle_response(response)

def update_product_stock(product_id: int, stock_data: dict):
    """Update product stock"""
    url = f"{API_URL}{ProductRoutes.UPDATE_PRODUCT_STOCK.value}"
    data = {"product_id": product_id, **stock_data}
    response = requests.put(url, json=data)
    return handle_response(response)

def delete_product(product_id: int):
    """Delete product"""
    url = f"{API_URL}{ProductRoutes.DELETE_PRODUCT.value}"
    data = {"product_id": product_id}
    response = requests.delete(url, json=data)
    return handle_response(response)

def get_products_by_category(category_id: int, page: int = 1, take: int = 10):
    """Get products by category with pagination using page number"""
    url = f"{API_URL}{ProductRoutes.PRODUCTS.value}"
    response = requests.get(url, params={
        "category_id": category_id,
        "page": page,
        "take": take
    })
    return handle_response(response)

def get_products_by_brand(brand_id: int, page: int = 1, take: int = 10, name: str = None, search: str = None):
    """Get products by brand with pagination using page number"""
    url = f"{API_URL}{ProductRoutes.PRODUCTS.value}"
    params = {
        "brand_id": brand_id,
        "page": page,
        "take": take
    }
    if name:
        params["name"] = name
    if search:
        params["search"] = search
    response = requests.get(url, params=params)
    return handle_response(response)

def search_products(keyword: str, category_id: int = None, page: int = 1, take: int = 10):
    """Search products by keyword and optional category with pagination"""
    url = f"{API_URL}{ProductRoutes.PRODUCTS.value}"
    params = {"keyword": keyword, "page": page, "take": take}
    if category_id:
        params["category_id"] = category_id
    response = requests.get(url, params=params)
    return handle_response(response)
