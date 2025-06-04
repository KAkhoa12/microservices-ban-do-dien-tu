from enum import Enum

class UserRoutes(str, Enum):
    LOGIN = "/api/user/login"
    REGISTER = "/api/user/register"
    ME = "/api/user/me"
    UPDATE_INFO = "/api/user/update-info"
    UPDATE_AVATAR = "/api/user/update-avatar"
    VALIDATE = "/api/user/validate"
    ADMIN_LIST_USER = "/api/user/admin/list-user"
    ADMIN_DELETE_USER = "/api/user/admin/delete-user"
    ADMIN_VALIDATE = "/api/user/admin/validate"

class BrandRoutes(str, Enum):
    BRANDS = "/api/brand/brands"
    CREATE_BRAND = "/api/brand/create-brand"
    UPDATE_INFO = "/api/brand/update-info"
    UPDATE_AVATAR = "/api/brand/update-avatar"
    DELETE_BRAND = "/api/brand/delete-brand"

class CategoryRoutes(str, Enum):
    CATEGORIES = "/api/category/categories"
    CREATE_CATEGORY = "/api/category/create-category"
    UPDATE_CATEGORY = "/api/category/update-category"
    UPDATE_CATEGORY_IMAGE = "/api/category/update-category-image"
    DELETE_CATEGORY = "/api/category/delete-category"

class ProductRoutes(str, Enum):
    PRODUCTS = "/api/product/products"
    CREATE_PRODUCT = "/api/product/create-product"
    UPDATE_PRODUCT = "/api/product/update-product"
    UPDATE_PRODUCT_IMAGE = "/api/product/update-product-image"
    DELETE_PRODUCT = "/api/product/delete-product"
    UPDATE_PRODUCT_STOCK = "/api/product/update-product-stock"

class CartRoutes(str, Enum):
    GET_CART = "/api/cart/get-cart"
    ADD_TO_CART = "/api/cart/add-to-cart"
    UPDATE_CART_ITEM = "/api/cart/update-cart-item"
    REMOVE_FROM_CART = "/api/cart/remove-from-cart"
    CLEAR_CART = "/api/cart/clear-cart"

class OrderRoutes(str, Enum):
    ORDERS = "/api/order/orders"
    GET_ORDER = "/api/order/get-order"
    CREATE_ORDER = "/api/order/create-order"
    CREATE_ORDER_FROM_CART = "/api/order/create-order-from-cart"
    UPDATE_ORDER = "/api/order/update-order"
    UPDATE_ORDER_STATUS = "/api/order/update-order-status"
    CANCEL_ORDER = "/api/order/cancel-order"
    DELETE_ORDER = "/api/order/delete-order"

class CongTrinhRoutes(str, Enum):
    LIST_CONG_TRINH = "/api/cong-trinh-toan-dien/list-cong-trinh"
    CREATE_CONG_TRINH = "/api/cong-trinh-toan-dien/create-cong-trinh"
    UPDATE_CONG_TRINH = "/api/cong-trinh-toan-dien/update-cong-trinh"
    UPDATE_CONG_TRINH_IMAGE = "/api/cong-trinh-toan-dien/update-cong-trinh-image"
    DELETE_CONG_TRINH = "/api/cong-trinh-toan-dien/delete-cong-trinh"
    GET_CONG_TRINH_ID = "/api/cong-trinh-toan-dien/get-cong-trinh-id"
    GET_CONG_TRINH_SLUG = "/api/cong-trinh-toan-dien/get-cong-trinh-slug"

class GiaiPhapRoutes(str, Enum):
    LIST_GIAI_PHAP = "/api/giai-phap-am-thanh/list-giai-phap"
    CREATE_GIAI_PHAP = "/api/giai-phap-am-thanh/create-giai-phap"
    UPDATE_GIAI_PHAP = "/api/giai-phap-am-thanh/update-giai-phap"
    UPDATE_GIAI_PHAP_IMAGE = "/api/giai-phap-am-thanh/update-giai-phap-image"
    DELETE_GIAI_PHAP = "/api/giai-phap-am-thanh/delete-giai-phap"
    GET_GIAI_PHAP_ID = "/api/giai-phap-am-thanh/get-giai-phap-id"
    GET_GIAI_PHAP_SLUG = "/api/giai-phap-am-thanh/get-giai-phap-slug"

class StaticFileRoutes(str, Enum):
    USER_IMAGES = "/static/user/imgs"
    BUSINESS_BRAND_LOGOS = "/static/business/brands"
    BUSINESS_PRODUCT_IMAGES = "/static/business/imgs"
