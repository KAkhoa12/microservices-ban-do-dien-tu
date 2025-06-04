# Import all services for easy access
from .base import handle_response, API_URL
from .user_service import (
    get_user_info,
    get_current_user,
    update_user_info,
    update_user_avatar,
    login_user,
    register_user
)
from .business_service import (
    get_all_brands,
    get_all_categories,
    get_all_products,
    get_product_by_id,
    get_products_by_category,
    get_products_by_brand,
    search_products
)
from .cart_service import (
    get_cart,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    clear_cart
)
from .cong_trinh_service import (
    get_cong_trinhs,
    get_cong_trinh_by_id,
    get_cong_trinh_by_slug
)
from .giai_phap_service import (
    get_giai_phaps,
    get_giai_phap_by_id,
    get_giai_phap_by_slug
)
from .order_service import (
    get_orders,
    get_order,
    create_order,
    create_order_from_cart,
    update_order_status,
    cancel_order
)

__all__ = [
    # Base
    'handle_response',
    'API_URL',
    # User services
    'get_user_info',
    'get_current_user',
    'update_user_info',
    'update_user_avatar',
    'login_user',
    'register_user',
    # Business services
    'get_all_brands',
    'get_all_categories',
    'get_all_products',
    'get_product_by_id',
    'get_products_by_category',
    'get_products_by_brand',
    'search_products',
    # Cart services
    'get_cart',
    'add_to_cart',
    'update_cart_item',
    'remove_from_cart',
    'clear_cart',
    # Cong Trinh services
    'get_cong_trinhs',
    'get_cong_trinh_by_id',
    'get_cong_trinh_by_slug',
    # Giai Phap services
    'get_giai_phaps',
    'get_giai_phap_by_id',
    'get_giai_phap_by_slug',
    # Order services
    'get_orders',
    'get_order',
    'create_order',
    'create_order_from_cart',
    'update_order_status',
    'cancel_order',
]
