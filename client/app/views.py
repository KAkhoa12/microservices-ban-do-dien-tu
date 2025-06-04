from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.cart_service import get_cart, add_to_cart, update_cart_item, remove_from_cart, clear_cart
from .services.order_service import (
    get_orders, get_order, create_order, create_order_from_cart,
    update_order_status, cancel_order, update_order, delete_order
)
from .services.cong_trinh_service import get_cong_trinhs, get_cong_trinh_by_id, get_cong_trinh_by_slug
from .services.giai_phap_service import get_giai_phaps, get_giai_phap_by_id, get_giai_phap_by_slug
from .services.user_service import register_user, get_current_user
from .services.base import handle_response
from .services.user_service import (
    get_user_info, login_user, update_user_info, update_user_avatar, register_user,
    get_all_users, get_user_by_id, create_user, update_user_by_admin, delete_user
)
from .services.business_service import (
    get_all_categories, get_category_by_id, create_category, update_category_info,
    update_category_image, delete_category, get_all_products, get_product_by_id,
    create_product, update_product_info, update_product_image, update_product_stock,
    delete_product, get_products_by_category, get_products_by_brand, search_products,
    get_all_brands, get_brand_by_id, create_brand, update_brand_info, update_brand_avatar, delete_brand
)
from .services.cache_service import get_cached_categories, get_cached_brands, get_cached_products, get_cached_product_by_id
from .services.payment_service import create_payment
from .decorator import admin_required, login_required, admin_cookie_required
from .utils.auth_utils import is_user_authenticated, get_user_from_cookies, is_user_admin, is_admin_authenticated, get_admin_from_cookies
import json



def safe_get_data(response, default=None):
    """Safely get data from response"""
    if not response:
        return default or {}
    return response.get('data', default or {})

def safe_get_payload(response, default=None):
    """Safely get payload from response data"""
    data = safe_get_data(response, default or {})
    if isinstance(data, dict):
        return data.get('items', default or [])
    return default or []


def safe_get_pagination(response):
    """Safely get pagination info from response data"""
    data = safe_get_data(response, {})
    if isinstance(data, dict):
        return {
            'total': data.get('total', 0),
            'page': data.get('page', 1),
            'take': data.get('take', 10),
            'total_pages': data.get('total_pages', 1)
        }
    return {'total': 0, 'page': 1, 'take': 10, 'total_pages': 1}

def get_category_by_id(category_id):
    """Get category by ID"""
    if not category_id:
        return {}
    response = get_all_categories(category_id=category_id, take=1)
    categories = safe_get_payload(response)
    return categories[0] if categories else {}

def get_brand_by_id(brand_id):
    """Get brand by ID"""
    if not brand_id:
        return {}
    response = get_all_brands(brand_id=brand_id, take=1)
    brands = safe_get_payload(response)
    return brands[0] if brands else {}

# View Front - End - Business Logic
def home_page(request):
    try:
        # Use cached data for better performance
        products_early_data = get_cached_products(take=10)
        products_top_selling_data = get_cached_products(take=10)
        brands = get_cached_brands()

        return render(request, 'frontend/pages/homepage.html', {
            'title': 'Trang chủ',
            'categories': [],  # Will be provided by global context processor
            '10_products_early': products_early_data.get('products', []) if isinstance(products_early_data, dict) else products_early_data,
            'products_top_selling': products_top_selling_data.get('products', []) if isinstance(products_top_selling_data, dict) else products_top_selling_data,
            'brands': brands
        })
    except Exception as e:
        messages.error(request, f"Error loading data: {str(e)}")
        return render(request, 'frontend/pages/homepage.html', {
            'title': 'Trang chủ',
            'categories': [],
            '10_products_early': [],
            'products_top_selling': [],
            'brands': []
        })

def all_categories_page(request):
    try:
        # Categories will be provided by global context processor
        return render(request, 'frontend/pages/all_categories.html', {
            'title': 'Tất cả danh mục',
            'categories': []  # Will be provided by global context processor
        })
    except Exception as e:
        messages.error(request, f"Error loading categories: {str(e)}")
        return render(request, 'frontend/pages/all_categories.html', {
            'title': 'Tất cả danh mục',
            'categories': []
        })

def all_products_by_category(request, id, page):
    try:
        # Use cached data for better performance
        products_data = get_cached_products(category_id=id, page=int(page), take=10)

        # Get specific category info using cache
        category_list = get_cached_categories(category_id=id, take=1)
        category = category_list[0] if category_list else {'id': id, 'name': 'Unknown Category'}

        # Extract products and pagination from cached data
        products = products_data.get('products', []) if isinstance(products_data, dict) else products_data
        pagination = products_data.get('pagination', {'total': 0, 'page': 1, 'take': 10, 'total_pages': 1}) if isinstance(products_data, dict) else {'total': 0, 'page': 1, 'take': 10, 'total_pages': 1}

        return render(request, 'frontend/pages/products_category.html', {
            'title': 'Danh sách sản phẩm',
            'categories': [],  # Will be provided by global context processor
            'category': category,
            'products': products,
            'current_page': int(page),
            'pagination': pagination,
            'pages': pagination['total_pages']  # Add pages for template compatibility
        })
    except Exception as e:
        messages.error(request, f"Error loading products: {str(e)}")
        return render(request, 'frontend/pages/products_category.html', {
            'title': 'Danh sách sản phẩm',
            'categories': [],
            'category': {'id': id, 'name': 'Unknown Category'},
            'products': [],
            'current_page': int(page),
            'pagination': {'total': 0, 'page': 1, 'take': 10, 'total_pages': 1},
            'pages': 1
        })

def thuonghieu_page(request):
    try:
        # Use cached brands for better performance
        brands = get_cached_brands()
        return render(request, 'frontend/pages/thuonghieu.html', {
            'title': 'Thương hiệu',
            'brands': brands,
            'categories': []  # Will be provided by global context processor
        })
    except Exception as e:
        messages.error(request, f"Error loading brands: {str(e)}")
        return render(request, 'frontend/pages/thuonghieu.html', {
            'title': 'Thương hiệu',
            'brands': [],
            'categories': []
        })

def products_brand_page(request, id, page=1):
    try:
        products = get_products_by_brand(id, page=int(page), take=10)
        # Get brand info by calling brands API with brand_id filter
        brand_response = get_all_brands(brand_id=id)
        brand_items = safe_get_payload(brand_response)
        brand = brand_items[0] if brand_items else {'id': id, 'name': 'Unknown Brand'}
        categories = get_all_categories()
        pagination = safe_get_pagination(products)

        return render(request, 'frontend/pages/products_brand.html', {
            'title': 'Danh sách sản phẩm',
            'brand': brand,
            'categories': safe_get_payload(categories),
            'products': safe_get_payload(products),
            'current_page': int(page),
            'pagination': pagination,
            'pages': pagination['total_pages']  # Add pages for template compatibility
        })
    except Exception as e:
        messages.error(request, f"Error loading products: {str(e)}")
        return render(request, 'frontend/pages/products_brand.html', {
            'title': 'Danh sách sản phẩm',
            'brand': {'id': id, 'name': 'Unknown Brand'},
            'categories': [],
            'products': [],
            'current_page': int(page),
            'pagination': {'total': 0, 'page': 1, 'take': 10, 'total_pages': 1},
            'pages': 1
        })

def search_page(request):
    try:
        if request.method == 'POST':
            keysearch = request.POST.get('keysearch')
            category_id = request.POST.get('category_id')
            categories = get_all_categories()
            products = get_all_products(search=keysearch, category_id=None if category_id == '0' else category_id)
            
            category_name = "Tất cả"
            if category_id and category_id != '0':
                category_response = get_all_categories(category_id)
                category_items = safe_get_payload(category_response)
                if category_items:
                    category_name = category_items[0].get('name', 'Tất cả')
                    
            return render(request, 'frontend/pages/search.html', {
                'title': 'Tìm kiếm', 
                'products': safe_get_payload(products),
                'categories': safe_get_payload(categories),
                'keysearch': keysearch,
                'category_name': category_name
            })
        
        categories = get_all_categories()
        return render(request, 'frontend/pages/search.html', {
            'title': 'Tìm kiếm',
            'categories': safe_get_payload(categories)
        })
    except Exception as e:
        messages.error(request, f"Error searching: {str(e)}")
        return render(request, 'frontend/pages/search.html', {
            'title': 'Tìm kiếm',
            'categories': []
        })

def product_page(request, id):
    try:
        # Use cached product data
        product_data = get_cached_product_by_id(id)

        # Use cached categories and brands
        category = {}
        brand = {}
        products_related = []

        if product_data.get('category_id'):
            category_list = get_cached_categories(category_id=product_data.get('category_id'), take=1)
            category = category_list[0] if category_list else {}

            # Get related products from same category
            related_data = get_cached_products(category_id=product_data.get('category_id'), take=4)
            products_related = related_data.get('products', []) if isinstance(related_data, dict) else related_data

        if product_data.get('brand_id'):
            brand_list = get_cached_brands(brand_id=product_data.get('brand_id'), take=1)
            brand = brand_list[0] if brand_list else {}

        return render(request, 'frontend/pages/product.html', {
            'title': product_data.get('name', ''),
            'product': product_data,
            'categories': [],  # Will be provided by global context processor
            'category': category,
            'brand': brand,
            'products_related': products_related
        })
    except Exception as e:
        messages.error(request, f"Error loading product: {str(e)}")
        return render(request, 'frontend/pages/product.html', {
            'title': 'Sản phẩm',
            'product': {},
            'categories': [],
            'category': {},
            'brand': {},
            'products_related': []
        })

def cart_page(request):
    # Check authentication using cookies and API
    if not is_user_authenticated(request):
        return redirect('login')

    try:
        user_data = get_user_from_cookies(request)
        categories = get_all_categories()
        cart = get_cart(user_data['id'])

        cart_data = safe_get_data(cart)
        cart_items = cart_data.get('cart', {}).get('cart_details', [])

        return render(request, 'frontend/pages/cart.html', {
            'title': 'Giỏ hàng',
            'categories': safe_get_payload(categories),
            'cart_details': cart_items,
            'cart_total': cart_data.get('total_price', 0),
            'user': user_data or {}
        })
    except Exception as e:
        messages.error(request, f"Error loading cart: {str(e)}")
        return render(request, 'frontend/pages/cart.html', {
            'title': 'Giỏ hàng',
            'categories': [],
            'cart_details': [],
            'user': {}
        })

def login_page(request):
    try:
        categories = get_all_categories()
        messages_list = []

        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            response = login_user(username, password)
            if response.get('status') == 'error':
                messages_list.append(response.get('message',response.get('message', 'Đăng nhập thất bại')))
            elif not response.get('data').get('user_role') == 'admin':
                # Đăng nhập thành công - lưu tokens vào cookies
                redirect_response = redirect('home')

                # Lấy tokens từ response
                data = response.get('data', {})
                access_token = data.get('access_token')
                refresh_token = data.get('refresh_token')

                if access_token:
                    # Set access_token cookie (7 days expiry)
                    redirect_response.set_cookie(
                        'access_token',
                        access_token,
                        max_age=7*24*60*60,  # 7 days in seconds
                        httponly=True,       # Prevent XSS
                        secure=False,        # Set to True in production with HTTPS
                        samesite='Lax'       # CSRF protection
                    )

                if refresh_token:
                    # Set refresh_token cookie (30 days expiry)
                    redirect_response.set_cookie(
                        'refresh_token',
                        refresh_token,
                        max_age=30*24*60*60,  # 30 days in seconds
                        httponly=True,        # Prevent XSS
                        secure=False,         # Set to True in production with HTTPS
                        samesite='Lax'        # CSRF protection
                    )

                # Không cần lưu session, chỉ dựa vào cookies và API /me

                return redirect_response
            else:
                messages_list.append(response.get('message',response.get('message', 'Đăng nhập thất bại')))

        return render(request, 'frontend/pages/login.html', {
            'title': 'Đăng nhập',
            'categories': safe_get_payload(categories),
            'messages': messages_list
        })
    except Exception as e:
        if request.method == 'POST':
            return JsonResponse({
                'status': 'error',
                'message': f"Error during login: {str(e)}"
            })
        messages.error(request, f"Error loading login page: {str(e)}")
        return render(request, 'frontend/pages/login.html', {
            'title': 'Đăng nhập',
            'categories': [],
            'messages': []
        })

def register_page(request):
    try:
        messages_list = []
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']
            re_password = request.POST['re_password']

            if password != re_password:
                messages_list.append("Mật khẩu nhập lại không đúng")
            else:
                # Sửa thứ tự tham số và thêm full_name (sử dụng username làm full_name mặc định)
                response = register_user(username, email, password, username)
                if response.get('status') == 'success':
                    # Đăng ký thành công, redirect về login để đăng nhập
                    messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
                    return redirect('login')
                else:
                    messages_list.append(response.get('message', 'Đăng ký thất bại'))

        categories = get_all_categories()
        return render(request, 'frontend/pages/register.html', {
            'title': 'Đăng ký',
            'categories': safe_get_payload(categories),
            'messages': messages_list
        })
    except Exception as e:
        messages.error(request, f"Error loading register page: {str(e)}")
        return render(request, 'frontend/pages/register.html', {
            'title': 'Đăng ký',
            'categories': [],
            'messages': []
        })

def get_user_with_token(request):
    """API endpoint to get user info with token and save to session"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            token = data.get('access_token')

            if not token:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Access token is required'
                })

            # Get user info using token
            from .services.user_service import get_current_user
            user_response = get_current_user(token)

            if user_response.get('status') == 'success':
                user_data = user_response.get('data', {})

                # Không lưu session, chỉ trả về user data
                return JsonResponse({
                    'status': 'success',
                    'message': 'User info retrieved successfully',
                    'data': user_data
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': user_response.get('message', 'Failed to get user info')
                })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f"Error getting user info: {str(e)}"
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method allowed'
    })

def logout_page(request):
    # Create redirect response
    response = redirect('home')

    # Delete cookies
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    return response


def get_cart_data_api(request):
    """API endpoint to get current user's cart data"""
    if not is_user_authenticated(request):
        return JsonResponse({
            'status': 'error',
            'message': 'User not authenticated'
        })

    try:
        user_data = get_user_from_cookies(request)
        if not user_data or not user_data.get('id'):
            return JsonResponse({
                'status': 'error',
                'message': 'User data not found'
            })

        cart_response = get_cart(user_data['id'])
        cart_data = safe_get_data(cart_response)

        # Debug logging
        print(f"DEBUG - Cart response: {cart_response}")
        print(f"DEBUG - Cart data: {cart_data}")

        cart_details = cart_data.get('cart', {}).get('cart_details', [])
        cart_quantity = len(cart_details)
        cart_total = cart_data.get('total_price', 0)

        # Debug logging
        print(f"DEBUG - Cart details: {cart_details}")
        print(f"DEBUG - Cart quantity: {cart_quantity}")
        print(f"DEBUG - Cart total: {cart_total}")

        return JsonResponse({
            'status': 'success',
            'data': {
                'cart_quantity': cart_quantity,
                'cart_details': cart_details,
                'cart_total': cart_total
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f"Error fetching cart data: {str(e)}"
        })

def add_to_cart_view(request, id):
    if not is_user_authenticated(request):
        return redirect('login')

    user_data = get_user_from_cookies(request)
    from .services.cart_service import add_to_cart
    response = add_to_cart(user_data['id'], id)
    if response.get('status') != 'success':
        messages.error(request, response.get('message', 'Thêm vào giỏ hàng thất bại'))

    return redirect(request.META.get('HTTP_REFERER', 'home'))

def remove_from_cart_view(request, id):
    if not is_user_authenticated(request):
        return redirect('login')

    user_data = get_user_from_cookies(request)
    from .services.cart_service import remove_from_cart
    response = remove_from_cart(user_data['id'], id)
    if response.get('status') != 'success':
        messages.error(request, response.get('message', 'Xóa khỏi giỏ hàng thất bại'))

    return redirect(request.META.get('HTTP_REFERER', 'home'))

def increase_cart_item(request, id):
    if not is_user_authenticated(request):
        return redirect('login')

    user_data = get_user_from_cookies(request)
    from .services.cart_service import update_cart_item
    current_cart = get_cart(user_data['id'])
    cart_data = safe_get_data(current_cart)
    cart_items = cart_data.get('cart', {}).get('cart_details', [])

    # Find current quantity
    current_quantity = 1
    for item in cart_items:
        if item.get('product_id') == id:
            current_quantity = item.get('quantity', 1) + 1
            break

    response = update_cart_item(user_data['id'], id, current_quantity)
    if response.get('status') != 'success':
        messages.error(request, response.get('message', 'Cập nhật giỏ hàng thất bại'))

    return redirect(request.META.get('HTTP_REFERER', 'cart'))

def decrease_cart_item(request, id):
    if not is_user_authenticated(request):
        return redirect('login')

    user_data = get_user_from_cookies(request)
    from .services.cart_service import update_cart_item
    current_cart = get_cart(user_data['id'])
    cart_data = safe_get_data(current_cart)
    cart_items = cart_data.get('cart', {}).get('cart_details', [])

    # Find current quantity
    current_quantity = 1
    for item in cart_items:
        if item.get('product_id') == id:
            current_quantity = max(1, item.get('quantity', 1) - 1)
            break

    response = update_cart_item(user_data['id'], id, current_quantity)
    if response.get('status') != 'success':
        messages.error(request, response.get('message', 'Cập nhật giỏ hàng thất bại'))

    return redirect(request.META.get('HTTP_REFERER', 'cart'))

def profile_page(request):
    if not is_user_authenticated(request):
        return redirect('login_page')

    try:
        user_data = get_user_from_cookies(request)
        categories = get_all_categories()

        return render(request, 'frontend/pages/profile.html', {
            'user': user_data or {},
            'categories': safe_get_payload(categories)
        })
    except Exception as e:
        messages.error(request, f"Error loading profile: {str(e)}")
        return render(request, 'frontend/pages/profile.html', {
            'user': {},
            'categories': []
        })

def update_user(request, user_id):
    # Check authentication first
    if not is_user_authenticated(request):
        return redirect('login_page')

    if request.method == 'POST':
        try:
            # Get current user data
            user_data = get_user_from_cookies(request)
            if not user_data:
                messages.error(request, 'Không thể lấy thông tin người dùng')
                return redirect('profile_page')

            # Use current user's ID if user_id doesn't match
            if user_id != user_data.get('id'):
                user_id = user_data.get('id')

            # Prepare data for API (match User Service schema)
            data = {
                'full_name': request.POST.get('name'),  # API expects 'full_name'
                'email': request.POST.get('email'),
                'phone_number': request.POST.get('phone'),  # API expects 'phone_number'
                'address': request.POST.get('address')
            }

            # Remove empty values
            data = {k: v for k, v in data.items() if v}

            # Xử lý mật khẩu nếu có
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password and confirm_password:
                if new_password != confirm_password:
                    messages.error(request, 'Mật khẩu mới và mật khẩu xác nhận không khớp')
                    return redirect('profile_page')
                data['current_password'] = current_password
                data['new_password'] = new_password

            # Xử lý ảnh đại diện trước
            image = request.FILES.get('image')
            if image:
                # Get access token from cookies
                access_token = request.COOKIES.get('access_token')
                response = update_user_avatar(user_id, image, access_token)
                if response.get('status') != 'success':
                    messages.error(request, response.get('message', 'Cập nhật ảnh đại diện thất bại'))
                    return redirect('profile_page')

            # Cập nhật thông tin
            if data:  # Only call API if there's data to update
                # Get access token from cookies
                access_token = request.COOKIES.get('access_token')
                response = update_user_info(user_id, data, access_token)
                if response.get('status') == 'success':
                    messages.success(request, 'Cập nhật thông tin thành công')
                else:
                    messages.error(request, response.get('message', 'Cập nhật thông tin thất bại'))
            else:
                messages.info(request, 'Không có thông tin nào được thay đổi')

        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật thông tin: {str(e)}')

    return redirect('profile_page')

def cong_trinh_toan_dien_page(request, id=None):
    try:
        categories = get_all_categories()
        cong_trinhs = get_cong_trinhs()
        
        if id:
            cong_trinh = get_cong_trinh_by_id(id)
        else:
            cong_trinh = safe_get_payload(cong_trinhs)[0] if safe_get_payload(cong_trinhs) else None
            
        return render(request, 'frontend/pages/cong_trinh_toan_dien.html', {
            'title': safe_get_data(cong_trinh).get('title', 'Công trình toàn diện') if cong_trinh else 'Công trình toàn diện',
            'categories': safe_get_payload(categories),
            'cong_trinh': safe_get_data(cong_trinh),
            'latest_cong_trinhs': safe_get_payload(cong_trinhs)[:5]
        })
    except Exception as e:
        messages.error(request, f"Error loading cong trinh: {str(e)}")
        return render(request, 'frontend/pages/cong_trinh_toan_dien.html', {
            'title': 'Công trình toàn diện',
            'categories': [],
            'cong_trinh': {},
            'latest_cong_trinhs': []
        })

def giai_phap_am_thanh_page(request, id=None):
    try:
        categories = get_all_categories()
        giai_phaps = get_giai_phaps()
        
        if id:
            giai_phap = get_giai_phap_by_id(id)
        else:
            giai_phap = safe_get_payload(giai_phaps)[0] if safe_get_payload(giai_phaps) else None
            
        return render(request, 'frontend/pages/giai_phap_am_thanh.html', {
            'title': safe_get_data(giai_phap).get('title', 'Giải pháp âm thanh') if giai_phap else 'Giải pháp âm thanh',
            'categories': safe_get_payload(categories),
            'giai_phap': safe_get_data(giai_phap),
            'giai_phaps': safe_get_payload(giai_phaps),
            'latest_giai_phaps': safe_get_payload(giai_phaps)[:5]
        })
    except Exception as e:
        messages.error(request, f"Error loading giai phap: {str(e)}")
        return render(request, 'frontend/pages/giai_phap_am_thanh.html', {
            'title': 'Giải pháp âm thanh',
            'categories': [],
            'giai_phap': {},
            'giai_phaps': [],
            'latest_giai_phaps': []
        })

def ve_chung_toi_page(request):
    try:
        categories = get_all_categories()
        return render(request, 'frontend/pages/ve_chung_toi.html', {
            'title': 'Về chúng tôi',
            'categories': safe_get_payload(categories)
        })
    except Exception as e:
        messages.error(request, f"Error loading about page: {str(e)}")
        return render(request, 'frontend/pages/ve_chung_toi.html', {
            'title': 'Về chúng tôi',
            'categories': []
        })

def test_auth_page(request):
    """Test page to debug authentication context"""
    return render(request, 'test_auth.html', {
        'title': 'Test Authentication'
    })

# Order views
def orders_page(request):
    """Display user's orders"""
    if not is_user_authenticated(request):
        return redirect('login')

    try:
        user_data = get_user_from_cookies(request)
        categories = get_all_categories()
        orders = get_orders(user_id=user_data['id'])

        return render(request, 'frontend/pages/order_history.html', {
            'title': 'Đơn hàng của tôi',
            'categories': safe_get_payload(categories),
            'orders': safe_get_payload(orders),
            'user': user_data or {}
        })
    except Exception as e:
        messages.error(request, f"Error loading orders: {str(e)}")
        return render(request, 'frontend/pages/order_history.html', {
            'title': 'Đơn hàng của tôi',
            'categories': [],
            'orders': [],
            'user': {}
        })

def order_detail_page(request, order_id):
    """Display order detail"""
    if not is_user_authenticated(request):
        return redirect('login')

    try:
        user_data = get_user_from_cookies(request)
        categories = get_all_categories()
        order = get_order(order_id)

        return render(request, 'frontend/pages/order_detail.html', {
            'title': 'Chi tiết đơn hàng',
            'categories': safe_get_payload(categories),
            'order': safe_get_data(order),
            'user': user_data or {}
        })
    except Exception as e:
        messages.error(request, f"Error loading order: {str(e)}")
        return render(request, 'frontend/pages/order_detail.html', {
            'title': 'Chi tiết đơn hàng',
            'categories': [],
            'order': {},
            'user': {}
        })

def checkout_page(request):
    """Checkout page"""
    if not is_user_authenticated(request):
        return redirect('login')

    try:
        user_data = get_user_from_cookies(request)
        categories = get_all_categories()
        cart = get_cart(user_data['id'])

        if request.method == 'POST':
            # Create order from cart
            response = create_order_from_cart(user_data['id'])
            if response.get('status') == 'success':
                messages.success(request, 'Đặt hàng thành công!')
                order_data = safe_get_data(response)
                return redirect('order_detail', order_id=order_data.get('id'))
            else:
                messages.error(request, response.get('message', 'Đặt hàng thất bại'))

        cart_data = safe_get_data(cart)
        cart_items = cart_data.get('cart', {}).get('cart_details', [])

        return render(request, 'frontend/pages/checkout.html', {
            'title': 'Thanh toán',
            'categories': safe_get_payload(categories),
            'cart_details': cart_items,
            'cart_total': cart_data.get('total_price', 0),
            'user': user_data or {}
        })
    except Exception as e:
        messages.error(request, f"Error loading checkout: {str(e)}")
        return render(request, 'frontend/pages/checkout.html', {
            'title': 'Thanh toán',
            'categories': [],
            'cart_details': [],
            'user': {}
        })

def cancel_order_view(request, order_id):
    """Cancel order view"""
    if not is_user_authenticated(request):
        return redirect('login')

    if request.method == 'POST':
        try:
            response = cancel_order(order_id)
            if response.get('status') == 'success':
                messages.success(request, 'Đơn hàng đã được hủy thành công!')
            else:
                messages.error(request, response.get('message', 'Hủy đơn hàng thất bại'))
        except Exception as e:
            messages.error(request, f"Lỗi khi hủy đơn hàng: {str(e)}")

    return redirect('order_history')

# ==================== PAYMENT VIEWS ====================

def create_payment_view(request):
    """
    Tạo thanh toán MoMo thông qua Payment Service
    """
    if request.method == 'POST':
        # Check authentication
        if not is_user_authenticated(request):
            messages.error(request, "Vui lòng đăng nhập để thực hiện thanh toán")
            return redirect('login')

        try:
            user_data = get_user_from_cookies(request)
            user_id = user_data['id']

            # Get cart data
            cart_response = get_cart(user_id)
            cart_data = safe_get_data(cart_response)
            cart_items = cart_data.get('cart', {}).get('cart_details', [])

            # Check if cart is empty
            if not cart_items:
                messages.error(request, "Giỏ hàng của bạn đang trống")
                return redirect('cart')

            # Validate user info
            required_fields = ['name', 'email', 'phone', 'address']
            missing_fields = []

            for field in required_fields:
                if not user_data.get(field):
                    missing_fields.append(field)

            if missing_fields:
                messages.error(request, f"Thiếu các giá trị trong các trường: {', '.join(missing_fields)}")
                return redirect('cart')

            # Get payment info
            amount = request.POST.get('amount')
            order_info = request.POST.get('order_info', 'Thanh toán đơn hàng')

            # Validate amount
            try:
                amount = int(float(amount))
            except (ValueError, TypeError):
                messages.error(request, "Số tiền không hợp lệ")
                return redirect('cart')

            # Call Payment Service to create payment
            result = create_payment(
                amount=amount,
                order_info=order_info,
                user_id=user_id,
                cart_data=cart_data
            )

            if result.get('status') == 'success':
                # Redirect to MoMo payment page
                payment_url = result.get('payment_url')
                if payment_url:
                    return redirect(payment_url)
                else:
                    messages.error(request, "Không nhận được URL thanh toán")
                    return redirect('cart')
            else:
                # Show error
                messages.error(request, result.get('message', 'Có lỗi xảy ra'))
                return redirect('cart')

        except Exception as e:
            messages.error(request, f'Lỗi xử lý thanh toán: {str(e)}')
            return redirect('cart')

    return redirect('cart')


# ==================== ADMIN BACKEND VIEWS ====================

def dashboard_login(request):
    try:
        messages_list = []
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            # Call User Service API for admin login
            response = login_user(username, password)

            if response.get('status') == 'success':
                # Get user data from response
                data = response.get('data', {})
                access_token = data.get('access_token')

                if access_token:
                    # Get user info to check if admin
                    user_response = get_current_user(access_token)

                    if user_response.get('status') == 'success':
                        user_data = user_response.get('data', {})

                        # Check if user is admin
                        if user_data.get('user_role') == 'admin':
                            # Set admin session and cookies
                            redirect_response = redirect('dashboard')

                            # Set access_token cookie for admin
                            redirect_response.set_cookie(
                                'admin_access_token',
                                access_token,
                                max_age=7*24*60*60,  # 7 days
                                httponly=True,
                                secure=False,
                                samesite='Lax'
                            )

                            # Set refresh_token if available
                            refresh_token = data.get('refresh_token')
                            if refresh_token:
                                redirect_response.set_cookie(
                                    'admin_refresh_token',
                                    refresh_token,
                                    max_age=30*24*60*60,  # 30 days
                                    httponly=True,
                                    secure=False,
                                    samesite='Lax'
                                )

                            return redirect_response
                        else:
                            messages_list.append("Bạn không có quyền truy cập admin")
                    else:
                        messages_list.append("Không thể lấy thông tin người dùng")
                else:
                    messages_list.append("Không nhận được token đăng nhập")
            else:
                messages_list.append(response.get('message', 'Đăng nhập thất bại'))

        return render(request, 'backend/pages/login.html', {
            'title': 'Đăng nhập Admin',
            'messages': messages_list
        })
    except Exception as e:
        messages.error(request, f"Error during admin login: {str(e)}")
        return render(request, 'backend/pages/login.html', {
            'title': 'Đăng nhập Admin',
            'messages': []
        })

@admin_required
def dashboard_logout(request):
    # Clear session (for backward compatibility)
    request.session.flush()

    # Create redirect response
    response = redirect('dashboard_login')

    # Clear admin cookies
    response.delete_cookie('admin_access_token')
    response.delete_cookie('admin_refresh_token')

    return response

@admin_cookie_required
def dashboard_page(request):
    try:
        # Get admin user data
        admin_data = get_admin_from_cookies(request)

        # Get statistics from Business Service
        categories_response = get_all_categories(take=1000)  # Get all to count
        brands_response = get_all_brands(take=1000)  # Get all to count
        products_response = get_all_products(take=1000)  # Get all to count

        # Count totals
        total_categories = len(safe_get_payload(categories_response))
        total_brands = len(safe_get_payload(brands_response))
        total_products = len(safe_get_payload(products_response))

        # For now, set default values for user and order statistics
        # These would need to be implemented in User Service and Business Service
        total_users = 0
        total_admin_users = 0
        total_normal_users = 0
        total_orders = 0
        pending_orders = 0
        completed_orders = 0
        cancelled_orders = 0
        total_revenue = 0
        top_products = []
        recent_orders = []

        # Chart data (empty for now)
        months = []
        orders_count = []
        orders_revenue = []
        order_status_labels = ['Đang xử lý', 'Hoàn thành', 'Đã hủy']
        order_status_data = [pending_orders, completed_orders, cancelled_orders]

        return render(request, 'backend/pages/dashboard.html', {
            'title': 'Dashboard Admin',
            'admin_user': admin_data,
            'total_products': total_products,
            'total_categories': total_categories,
            'total_brands': total_brands,
            'total_users': total_users,
            'total_admin_users': total_admin_users,
            'total_normal_users': total_normal_users,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': total_revenue,
            'top_products': top_products,
            'recent_orders': recent_orders,
            'months': months,
            'orders_count': orders_count,
            'orders_revenue': orders_revenue,
            'order_status_labels': order_status_labels,
            'order_status_data': order_status_data
        })
    except Exception as e:
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return render(request, 'backend/pages/dashboard.html', {
            'title': 'Dashboard Admin',
            'total_products': 0,
            'total_categories': 0,
            'total_brands': 0,
            'total_users': 0,
            'total_admin_users': 0,
            'total_normal_users': 0,
            'total_orders': 0,
            'pending_orders': 0,
            'completed_orders': 0,
            'cancelled_orders': 0,
            'total_revenue': 0,
            'top_products': [],
            'recent_orders': [],
            'months': [],
            'orders_count': [],
            'orders_revenue': [],
            'order_status_labels': ['Đang xử lý', 'Hoàn thành', 'Đã hủy'],
            'order_status_data': [0, 0, 0]
        })
        

# ==================== ADMIN PRODUCT MANAGEMENT ====================

@admin_cookie_required
def admin_products(request):
    try:
        response = get_all_products(take=99999)  # Get all products for admin
        products = safe_get_payload(response)

        return render(request, 'backend/pages/products/list.html', {
            'title': 'Quản lý sản phẩm',
            'products': products
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi tải danh sách sản phẩm: {str(e)}")
        return render(request, 'backend/pages/products/list.html', {
            'title': 'Quản lý sản phẩm',
            'products': []
        })

@admin_cookie_required
def admin_product_detail(request, id):
    try:
        # Get product details
        product_response = get_product_by_id(id)
        product = safe_get_payload(product_response)

        if not product:
            messages.error(request, 'Không tìm thấy sản phẩm')
            return redirect('admin_products')

        if request.method == 'POST':
            # Prepare update data
            update_data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description'),
                'price': float(request.POST.get('price', 0)),
                'old_price': float(request.POST.get('old_price', 0)) if request.POST.get('old_price') else None,
                'stock': int(request.POST.get('stock', 0)),
                'category_id': int(request.POST.get('category')),
                'brand_id': int(request.POST.get('brand'))
            }

            # Handle image upload
            if 'image' in request.FILES:
                # TODO: Implement file upload service
                # update_data['image_url'] = upload_file_to_service(request.FILES['image'], 'products')
                pass

            # Call Business Service API to update product
            update_response = update_product_info(id, update_data)
            if update_response.get('status') == 'success':
                messages.success(request, 'Cập nhật sản phẩm thành công')
                return redirect('admin_product_detail', id=id)
            else:
                messages.error(request, update_response.get('message', 'Cập nhật thất bại'))

        # Get categories and brands for form
        categories_response = get_all_categories(take=1000)
        brands_response = get_all_brands(take=1000)

        categories = safe_get_payload(categories_response)
        brands = safe_get_payload(brands_response)

        return render(request, 'backend/pages/products/detail.html', {
            'title': 'Chi tiết sản phẩm',
            'product': product,
            'categories': categories,
            'brands': brands
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi tải chi tiết sản phẩm: {str(e)}")
        return redirect('admin_products')

@admin_cookie_required
def admin_product_add(request):
    try:
        if request.method == 'POST':
            # Prepare product data
            product_data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description'),
                'price': float(request.POST.get('price', 0)),
                'old_price': float(request.POST.get('old_price', 0)) if request.POST.get('old_price') else None,
                'stock': int(request.POST.get('stock', 0)),
                'category_id': int(request.POST.get('category')),
                'brand_id': int(request.POST.get('brand'))
            }

            # Handle image upload
            if 'image' in request.FILES:
                # TODO: Implement file upload service
                # product_data['image_url'] = upload_file_to_service(request.FILES['image'], 'products')
                pass

            # Call Business Service API to create product
            create_response = create_product(product_data)
            if create_response.get('status') == 'success':
                messages.success(request, 'Thêm sản phẩm thành công')
                return redirect('admin_products')
            else:
                messages.error(request, create_response.get('message', 'Thêm sản phẩm thất bại'))

        # Get categories and brands for form
        categories_response = get_all_categories(take=1000)
        brands_response = get_all_brands(take=1000)

        categories = safe_get_payload(categories_response)
        brands = safe_get_payload(brands_response)

        return render(request, 'backend/pages/products/add.html', {
            'title': 'Thêm sản phẩm',
            'categories': categories,
            'brands': brands
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi thêm sản phẩm: {str(e)}")
        return redirect('admin_products')

@admin_cookie_required
def admin_product_delete(request, id):
    try:
        # Get product details for confirmation
        product_response = get_product_by_id(id)
        product = safe_get_payload(product_response)

        if not product:
            messages.error(request, 'Không tìm thấy sản phẩm')
            return redirect('admin_products')

        if request.method == 'POST':
            # Call Business Service API to delete product
            delete_response = delete_product(id)
            if delete_response.get('status') == 'success':
                messages.success(request, 'Xóa sản phẩm thành công')
                return redirect('admin_products')
            else:
                messages.error(request, delete_response.get('message', 'Xóa sản phẩm thất bại'))

        return render(request, 'backend/pages/products/delete.html', {
            'title': 'Xóa sản phẩm',
            'product': product
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi xóa sản phẩm: {str(e)}")
        return redirect('admin_products')

# ==================== ADMIN BRAND MANAGEMENT ====================

@admin_cookie_required
def admin_brands(request):
    try:
        response = get_all_brands(take=1000)  # Get all brands for admin
        brands = safe_get_payload(response)

        return render(request, 'backend/pages/brands/list.html', {
            'title': 'Quản lý thương hiệu',
            'brands': brands
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi tải danh sách thương hiệu: {str(e)}")
        return render(request, 'backend/pages/brands/list.html', {
            'title': 'Quản lý thương hiệu',
            'brands': []
        })

@admin_cookie_required
def admin_brand_detail(request, id):
    try:
        # Get brand details
        brand_response = get_brand_by_id(id)
        brand = safe_get_payload(brand_response)

        if not brand:
            messages.error(request, 'Không tìm thấy thương hiệu')
            return redirect('admin_brands')

        if request.method == 'POST':
            # Prepare update data
            update_data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description', ''),
                'slug': request.POST.get('slug', '')
            }

            # Handle image upload
            if 'image' in request.FILES:
                # TODO: Implement file upload service
                # update_data['image_url'] = upload_file_to_service(request.FILES['image'], 'brands')
                pass

            # Call Business Service API to update brand
            update_response = update_brand_info(id, update_data)
            if update_response.get('status') == 'success':
                messages.success(request, 'Cập nhật thương hiệu thành công')
                return redirect('admin_brand_detail', id=id)
            else:
                messages.error(request, update_response.get('message', 'Cập nhật thất bại'))

        return render(request, 'backend/pages/brands/detail.html', {
            'title': 'Chi tiết thương hiệu',
            'brand': brand
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi tải chi tiết thương hiệu: {str(e)}")
        return redirect('admin_brands')

@admin_cookie_required
def admin_brand_add(request):
    try:
        if request.method == 'POST':
            # Prepare brand data
            brand_data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description', ''),
                'slug': request.POST.get('slug', '')
            }

            # Handle image upload
            if 'image' in request.FILES:
                # TODO: Implement file upload service
                # brand_data['image_url'] = upload_file_to_service(request.FILES['image'], 'brands')
                pass

            # Call Business Service API to create brand
            create_response = create_brand(brand_data)
            if create_response.get('status') == 'success':
                messages.success(request, 'Thêm thương hiệu thành công')
                return redirect('admin_brands')
            else:
                messages.error(request, create_response.get('message', 'Thêm thương hiệu thất bại'))

        return render(request, 'backend/pages/brands/add.html', {
            'title': 'Thêm thương hiệu'
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi thêm thương hiệu: {str(e)}")
        return redirect('admin_brands')

@admin_cookie_required
def admin_brand_delete(request, id):
    try:
        # Get brand details for confirmation
        brand_response = get_brand_by_id(id)
        brand = safe_get_payload(brand_response)

        if not brand:
            messages.error(request, 'Không tìm thấy thương hiệu')
            return redirect('admin_brands')

        if request.method == 'POST':
            # Call Business Service API to delete brand
            delete_response = delete_brand(id)
            if delete_response.get('status') == 'success':
                messages.success(request, 'Xóa thương hiệu thành công')
                return redirect('admin_brands')
            else:
                messages.error(request, delete_response.get('message', 'Xóa thương hiệu thất bại'))

        return render(request, 'backend/pages/brands/delete.html', {
            'title': 'Xóa thương hiệu',
            'brand': brand
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi xóa thương hiệu: {str(e)}")
        return redirect('admin_brands')

# ==================== ADMIN CATEGORY MANAGEMENT ====================

@admin_cookie_required
def admin_categories(request):
    try:
        response = get_all_categories(take=1000)  # Get all categories for admin
        categories = safe_get_payload(response)

        return render(request, 'backend/pages/categories/list.html', {
            'title': 'Quản lý danh mục',
            'categories': categories
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi tải danh sách danh mục: {str(e)}")
        return render(request, 'backend/pages/categories/list.html', {
            'title': 'Quản lý danh mục',
            'categories': []
        })

@admin_cookie_required
def admin_category_detail(request, id):
    try:
        # Get category details
        category_response = get_category_by_id(id)
        category = safe_get_payload(category_response)

        if not category:
            messages.error(request, 'Không tìm thấy danh mục')
            return redirect('admin_categories')

        if request.method == 'POST':
            # Prepare update data
            update_data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description', ''),
                'slug': request.POST.get('slug', '')
            }

            # Handle image upload
            if 'image' in request.FILES:
                # TODO: Implement file upload service
                # update_data['image_url'] = upload_file_to_service(request.FILES['image'], 'categories')
                pass

            # Call Business Service API to update category
            update_response = update_category_info(id, update_data)
            if update_response.get('status') == 'success':
                messages.success(request, 'Cập nhật danh mục thành công')
                return redirect('admin_category_detail', id=id)
            else:
                messages.error(request, update_response.get('message', 'Cập nhật thất bại'))

        return render(request, 'backend/pages/categories/detail.html', {
            'title': 'Chi tiết danh mục',
            'category': category
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi tải chi tiết danh mục: {str(e)}")
        return redirect('admin_categories')

@admin_cookie_required
def admin_category_add(request):
    try:
        if request.method == 'POST':
            # Prepare category data
            category_data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description', ''),
                'slug': request.POST.get('slug', '')
            }

            # Handle image upload
            if 'image' in request.FILES:
                # TODO: Implement file upload service
                # category_data['image_url'] = upload_file_to_service(request.FILES['image'], 'categories')
                pass

            # Call Business Service API to create category
            create_response = create_category(category_data)
            if create_response.get('status') == 'success':
                messages.success(request, 'Thêm danh mục thành công')
                return redirect('admin_categories')
            else:
                messages.error(request, create_response.get('message', 'Thêm danh mục thất bại'))

        return render(request, 'backend/pages/categories/add.html', {
            'title': 'Thêm danh mục'
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi thêm danh mục: {str(e)}")
        return redirect('admin_categories')

@admin_cookie_required
def admin_category_delete(request, id):
    try:
        # Get category details for confirmation
        category_response = get_category_by_id(id)
        category = safe_get_payload(category_response)

        if not category:
            messages.error(request, 'Không tìm thấy danh mục')
            return redirect('admin_categories')

        if request.method == 'POST':
            # Call Business Service API to delete category
            delete_response = delete_category(id)
            if delete_response.get('status') == 'success':
                messages.success(request, 'Xóa danh mục thành công')
                return redirect('admin_categories')
            else:
                messages.error(request, delete_response.get('message', 'Xóa danh mục thất bại'))

        return render(request, 'backend/pages/categories/delete.html', {
            'title': 'Xóa danh mục',
            'category': category
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi xóa danh mục: {str(e)}")
        return redirect('admin_categories')

# ==================== ADMIN USER MANAGEMENT ====================

@admin_cookie_required
def admin_users(request):
    try:
        response = get_all_users(take=1000)  # Get all users for admin
        users = safe_get_payload(response)

        return render(request, 'backend/pages/users/list.html', {
            'title': 'Quản lý người dùng',
            'users': users
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi tải danh sách người dùng: {str(e)}")
        return render(request, 'backend/pages/users/list.html', {
            'title': 'Quản lý người dùng',
            'users': []
        })

@admin_cookie_required
def admin_user_detail(request, id):
    try:
        # Get user details
        user_response = get_user_by_id(id)
        user = safe_get_payload(user_response)

        if not user:
            messages.error(request, 'Không tìm thấy người dùng')
            return redirect('admin_users')

        if request.method == 'POST':
            # Prepare update data
            update_data = {
                'username': request.POST.get('username'),
                'email': request.POST.get('email'),
                'name': request.POST.get('name'),
                'phone': request.POST.get('phone'),
                'address': request.POST.get('address'),
                'role': request.POST.get('role')
            }

            # Handle password update
            password = request.POST.get('password')
            if password:
                update_data['password'] = password

            # Handle image upload
            if 'image' in request.FILES:
                # TODO: Implement file upload service
                # update_data['image_url'] = upload_file_to_service(request.FILES['image'], 'users')
                pass

            # Call User Service API to update user
            update_response = update_user_by_admin(id, update_data)
            if update_response.get('status') == 'success':
                messages.success(request, 'Cập nhật người dùng thành công')
                return redirect('admin_users')
            else:
                messages.error(request, update_response.get('message', 'Cập nhật thất bại'))

        return render(request, 'backend/pages/users/detail.html', {
            'title': 'Chi tiết người dùng',
            'user': user
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi tải chi tiết người dùng: {str(e)}")
        return redirect('admin_users')

@admin_cookie_required
def admin_user_add(request):
    try:
        if request.method == 'POST':
            # Prepare user data
            user_data = {
                'username': request.POST.get('username'),
                'email': request.POST.get('email'),
                'password': request.POST.get('password'),
                'name': request.POST.get('name'),
                'phone': request.POST.get('phone'),
                'address': request.POST.get('address'),
                'role': request.POST.get('role')
            }

            # Handle image upload
            if 'image' in request.FILES:
                # TODO: Implement file upload service
                # user_data['image_url'] = upload_file_to_service(request.FILES['image'], 'users')
                pass

            # Call User Service API to create user
            create_response = create_user(user_data)
            if create_response.get('status') == 'success':
                messages.success(request, 'Thêm người dùng thành công')
                return redirect('admin_users')
            else:
                messages.error(request, create_response.get('message', 'Thêm người dùng thất bại'))

        return render(request, 'backend/pages/users/add.html', {
            'title': 'Thêm người dùng'
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi thêm người dùng: {str(e)}")
        return redirect('admin_users')

@admin_cookie_required
def admin_user_delete(request, user_id):
    try:
        if request.method == 'POST':
            # Call User Service API to delete user
            delete_response = delete_user(user_id)
            if delete_response.get('status') == 'success':
                messages.success(request, 'Xóa người dùng thành công')
            else:
                messages.error(request, delete_response.get('message', 'Xóa người dùng thất bại'))

        return redirect('admin_users')
    except Exception as e:
        messages.error(request, f"Lỗi khi xóa người dùng: {str(e)}")
        return redirect('admin_users')

# Công trình toàn diện
@admin_required
def admin_cong_trinh(request):
    cong_trinhs = CongTrinhToanDien.objects.all()
    return render(request, 'backend/pages/cong_trinh/list.html', {'cong_trinhs': cong_trinhs})

@admin_required
def admin_cong_trinh_detail(request, id):
    cong_trinh = get_object_or_404(CongTrinhToanDien, id=id)
    
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            content = request.POST.get('content')
            status = request.POST.get('status')
            
            # Kiểm tra dữ liệu bắt buộc
            if not title or not description or not content:
                messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc')
                return render(request, 'backend/pages/cong_trinh/detail.html', {'cong_trinh': cong_trinh})
            
            # Cập nhật thông tin
            cong_trinh.title = title
            cong_trinh.description = description
            cong_trinh.content = content
            
            # Xử lý upload ảnh mới nếu có
            if 'image' in request.FILES and request.FILES['image']:
                cong_trinh.image_url = upload_file.upload_file(request.FILES['image'], 'cong_trinh')
            cong_trinh.status = status
            # Lưu thay đổi
            cong_trinh.save()
            messages.success(request, 'Cập nhật công trình thành công')
            return redirect('admin_cong_trinh')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return render(request, 'backend/pages/cong_trinh/detail.html', {'cong_trinh': cong_trinh})
    
    return render(request, 'backend/pages/cong_trinh/detail.html', {'cong_trinh': cong_trinh})

@admin_required
def admin_cong_trinh_add(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            content = request.POST.get('content')
            
            # Kiểm tra dữ liệu bắt buộc
            if not title or not description or not content:
                messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc')
                return render(request, 'backend/pages/cong_trinh/add.html')
            
            # Tạo công trình mới
            cong_trinh = CongTrinhToanDien(
                title=title,
                description=description,
                content=content,
                author_id=request.session['user_id'],
                status='active'
            )
            
            # Xử lý upload ảnh
            if 'image' in request.FILES:
                cong_trinh.image_url = upload_file.upload_file(request.FILES['image'], 'cong_trinh')
            else:
                messages.error(request, 'Vui lòng chọn hình ảnh cho công trình')
                return render(request, 'backend/pages/cong_trinh/add.html')
            
            # Lưu công trình
            cong_trinh.save()
            messages.success(request, 'Thêm công trình thành công')
            return redirect('admin_cong_trinh')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return render(request, 'backend/pages/cong_trinh/add.html')
    
    return render(request, 'backend/pages/cong_trinh/add.html')

@admin_required
def admin_cong_trinh_delete(request, id):
    try:
        cong_trinh = CongTrinhToanDien.objects.get(id=id)
        # Xóa file ảnh nếu có
        if cong_trinh.image_url:
            try:
                image_path = os.path.join(settings.MEDIA_ROOT, str(cong_trinh.image_url))
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Lỗi khi xóa file ảnh: {str(e)}")
        
        cong_trinh.delete()
        messages.success(request, 'Đã xóa công trình thành công!')
    except CongTrinhToanDien.DoesNotExist:
        messages.error(request, 'Không tìm thấy công trình cần xóa!')
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra khi xóa công trình: {str(e)}')
    
    return redirect('admin_cong_trinh')

# Giải pháp âm thanh
@admin_required
def admin_giai_phap(request):
    giai_phaps = GiaiPhapAmThanh.objects.all()
    return render(request, 'backend/pages/giai_phap/list.html', {'giai_phaps': giai_phaps})

@admin_required
def admin_giai_phap_detail(request, id):
    giai_phap = get_object_or_404(GiaiPhapAmThanh, id=id)
    
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            content = request.POST.get('content')
            youtube_url = request.POST.get('youtube_url', '')
            
            # Kiểm tra dữ liệu bắt buộc
            if not title or not description or not content:
                messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc')
                return render(request, 'backend/pages/giai_phap/detail.html', {'giai_phap': giai_phap})
            
            # Cập nhật thông tin
            giai_phap.title = title
            giai_phap.description = description
            giai_phap.content = content
            giai_phap.youtube_url = youtube_url
            
            # Xử lý upload ảnh mới nếu có
            if 'image' in request.FILES and request.FILES['image']:
                giai_phap.image_url = upload_file.upload_file(request.FILES['image'], 'giai_phap')
            
            # Lưu thay đổi
            giai_phap.save()
            messages.success(request, 'Cập nhật giải pháp thành công')
            return redirect('admin_giai_phap')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return render(request, 'backend/pages/giai_phap/detail.html', {'giai_phap': giai_phap})
    
    return render(request, 'backend/pages/giai_phap/detail.html', {'giai_phap': giai_phap})

@admin_required
def admin_giai_phap_add(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            content = request.POST.get('content')
            youtube_url = request.POST.get('youtube_url', '')
            
            # Kiểm tra dữ liệu bắt buộc
            if not title or not description or not content:
                messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc')
                return render(request, 'backend/pages/giai_phap/add.html')
            
            # Tạo giải pháp mới
            giai_phap = GiaiPhapAmThanh(
                title=title,
                description=description,
                content=content,
                youtube_url=youtube_url,
                author_id=request.session['user_id'],
                status='active'
            )
            
            # Xử lý upload ảnh
            if 'image' in request.FILES:
                giai_phap.image_url = upload_file.upload_file(request.FILES['image'], 'giai_phap')
            else:
                messages.error(request, 'Vui lòng chọn hình ảnh cho giải pháp')
                return render(request, 'backend/pages/giai_phap/add.html')
            
            # Lưu giải pháp
            giai_phap.save()
            messages.success(request, 'Thêm giải pháp thành công')
            return redirect('admin_giai_phap')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return render(request, 'backend/pages/giai_phap/add.html')
    
    return render(request, 'backend/pages/giai_phap/add.html')

@admin_required
def admin_giai_phap_delete(request, giai_phap_id):
    try:
        giai_phap = GiaiPhapAmThanh.objects.get(id=giai_phap_id)
        # Xóa file ảnh nếu có
        if giai_phap.image_url:
            try:
                image_path = os.path.join(settings.MEDIA_ROOT, str(giai_phap.image_url))
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Lỗi khi xóa file ảnh: {str(e)}")
        
        giai_phap.delete()
        messages.success(request, 'Đã xóa giải pháp thành công!')
    except GiaiPhapAmThanh.DoesNotExist:
        messages.error(request, 'Không tìm thấy giải pháp cần xóa!')
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra khi xóa giải pháp: {str(e)}')
    
    return redirect('admin_giai_phap')

@admin_required
def dashboard_logout(request):
    request.session.flush()
    return redirect('dashboard_login')

# ==================== ADMIN ORDER MANAGEMENT ====================

@admin_cookie_required
def admin_orders(request):
    try:
        response = get_orders(take=1000)  # Get all orders for admin
        orders_data = safe_get_payload(response)
        orders = orders_data.get('items', []) if isinstance(orders_data, dict) else orders_data

        return render(request, 'backend/pages/orders/list.html', {
            'title': 'Quản lý đơn hàng',
            'orders': orders
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi tải danh sách đơn hàng: {str(e)}")
        return render(request, 'backend/pages/orders/list.html', {
            'title': 'Quản lý đơn hàng',
            'orders': []
        })

@admin_cookie_required
def admin_order_detail(request, id):
    try:
        # Get order details
        order_response = get_order(id)
        order = safe_get_payload(order_response)

        if not order:
            messages.error(request, 'Không tìm thấy đơn hàng')
            return redirect('admin_orders')

        if request.method == 'POST':
            # Update order status
            new_status = request.POST.get('status')
            if new_status:
                update_response = update_order_status(id, new_status)
                if update_response.get('status') == 'success':
                    messages.success(request, 'Cập nhật trạng thái đơn hàng thành công')
                    return redirect('admin_order_detail', id=id)
                else:
                    messages.error(request, update_response.get('message', 'Cập nhật thất bại'))

        return render(request, 'backend/pages/orders/detail.html', {
            'title': 'Chi tiết đơn hàng',
            'order': order,
            'order_details': order.get('order_details', [])
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi tải chi tiết đơn hàng: {str(e)}")
        return redirect('admin_orders')

@admin_cookie_required
def admin_order_delete(request, id):
    try:
        # Get order details for confirmation
        order_response = get_order(id)
        order = safe_get_payload(order_response)

        if not order:
            messages.error(request, 'Không tìm thấy đơn hàng')
            return redirect('admin_orders')

        if request.method == 'POST':
            # Call Order Service API to delete order
            delete_response = delete_order(id)
            if delete_response.get('status') == 'success':
                messages.success(request, 'Xóa đơn hàng thành công')
                return redirect('admin_orders')
            else:
                messages.error(request, delete_response.get('message', 'Xóa đơn hàng thất bại'))

        return render(request, 'backend/pages/orders/delete.html', {
            'title': 'Xóa đơn hàng',
            'order': order
        })
    except Exception as e:
        messages.error(request, f"Lỗi khi xóa đơn hàng: {str(e)}")
        return redirect('admin_orders')

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Gọi hàm xử lý tin nhắn của chatbot
            response = process_message(user_message)
            
            # Nếu response có type là "list", lấy thông tin sản phẩm từ sources
            if response.get('type') == 'list':
                product_ids = [source['id'] for source in response.get('sources', [])]
                products = Product.objects.filter(id__in=product_ids)
                
                products_data = []
                for product in products:
                    products_data.append({
                        'id': product.id,
                        'name': product.name,
                        'price': str(product.price),
                        'image_url': product.image_url,
                        'description': product.description,
                        'brand': product.brand.name if product.brand else None,
                        'category': product.category.name if product.category else None,
                        'url': f'/product/{product.id}'
                    })
                
                return JsonResponse({
                    'status': 'success',
                    'response': {
                        'answer': response.get('answer', ''),
                        'sources': products_data
                    }
                })
            
            # Trả về response thông thường nếu không phải type list
            return JsonResponse({
                'status': 'success',
                'response': response
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            })
            
    return JsonResponse({
        'status': 'error',
        'message': 'Chỉ hỗ trợ phương thức POST'
    })

def handle_general_questions(question):
    """Xử lý các câu hỏi chào hỏi và câu hỏi thông thường"""
    question_lower = question.lower().strip()
    
    # Xử lý các câu chào
    greetings = ["hi", "hello", "chào", "xin chào", "hey", "hi there", "chào bạn"]
    if any(greeting == question_lower for greeting in greetings):
        return "Xin chào! Tôi là trợ lý ảo về thiết bị âm thanh, tôi có thể giúp bạn tìm kiếm thông tin về sản phẩm, giá cả, thương hiệu. Bạn cần hỏi gì về thiết bị âm thanh?"
    
    # Xử lý câu hỏi về tên
    name_questions = ["tên bạn là gì", "bạn tên gì", "tên của bạn là gì", "bạn là ai", "what is your name", "who are you"]
    if any(name_question in question_lower for name_question in name_questions):
        return "Tôi là trợ lý AI chuyên về thiết bị âm thanh của DoAn_QuanLyDoDienTu. Tôi có thể giúp bạn tìm kiếm thông tin về các sản phẩm âm thanh, giá cả, và thương hiệu. Bạn cần hỏi gì về thiết bị âm thanh?"
    
    # Xử lý cảm ơn
    thanks = ["cảm ơn", "thank", "thanks", "cám ơn"]
    if any(thank_word in question_lower for thank_word in thanks):
        return "Không có gì! Rất vui khi được giúp đỡ bạn. Bạn có câu hỏi nào khác về thiết bị âm thanh không?"
    
    # Xử lý tạm biệt
    goodbyes = ["tạm biệt", "bye", "goodbye", "gặp lại sau"]
    if any(goodbye in question_lower for goodbye in goodbyes):
        return "Tạm biệt! Rất vui được giúp đỡ bạn. Hẹn gặp lại bạn lần sau!"
    
    # Xử lý câu hỏi về khả năng của chatbot
    capabilities = ["bạn có thể làm gì", "bạn giúp được gì", "chức năng của bạn", "bạn biết gì"]
    if any(capability in question_lower for capability in capabilities):
        return "Tôi có thể giúp bạn tìm kiếm thông tin về các sản phẩm âm thanh như loa, amply, tai nghe... Tôi cũng có thể cung cấp thông tin về giá cả, thương hiệu, tính năng và so sánh các sản phẩm. Bạn có thể hỏi tôi về bất kỳ sản phẩm âm thanh nào!"
    
    # Nếu không thuộc các trường hợp trên, trả về None để xử lý như câu hỏi về sản phẩm
    return None

def handle_combined_query(question):
    """Xử lý truy vấn kết hợp giữa hãng và các tiêu chí khác"""
    question_lower = question.lower()
    
    # Kiểm tra xem có đề cập đến hãng nào không
    brands = ["JBL", "Sony", "Denon", "Yamaha", "Bose", "Sennheiser", "Audio-Technica", 
              "KEF", "Klipsch", "Polk Audio", "Cambridge Audio", "Boston Acoustics", 
              "Harman Kardon", "Marshall", "Bang & Olufsen", "Focal", "Dynaudio"]
    
    found_brand = None
    for brand in brands:
        if brand.lower() in question_lower:
            found_brand = brand
            break
    
    # Nếu không tìm thấy thương hiệu, trả về None
    if not found_brand:
        return None
    
    # Kiểm tra các tiêu chí khác
    is_top_selling = any(term in question_lower for term in ["bán chạy", "mua nhiều", "bán nhiều"])
    is_most_liked = any(term in question_lower for term in ["yêu thích", "ưa chuộng", "nhiều like", "được yêu thích"])
    is_highest_price = any(term in question_lower for term in ["đắt nhất", "cao nhất", "giá cao"])
    is_lowest_price = any(term in question_lower for term in ["rẻ nhất", "thấp nhất", "giá thấp"])
    
    # Tạo truy vấn kết hợp
    if is_top_selling:
        return f"Tên hãng: {found_brand} sản phẩm có số lượng mua nhiều nhất"
    elif is_most_liked:
        return f"Tên hãng: {found_brand} sản phẩm có số lượng like nhiều nhất"
    elif is_highest_price:
        return f"Tên hãng: {found_brand} sản phẩm có giá cao nhất"
    elif is_lowest_price:
        return f"Tên hãng: {found_brand} sản phẩm có giá thấp nhất"
    
    # Nếu chỉ có thương hiệu mà không có tiêu chí cụ thể
    return f"Tên hãng: {found_brand}"

@csrf_exempt
def get_products_by_ids(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_ids = data.get('product_ids', [])
            
            # Lấy danh sách sản phẩm từ các ID
            products = Product.objects.filter(id__in=product_ids)
            
            # Chuyển đổi queryset thành list các dictionary
            products_data = []
            for product in products:
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'price': str(product.price),
                    'image_url': product.image_url,
                    'description': product.description,
                    'brand': product.brand.name if product.brand else None,
                    'category': product.category.name if product.category else None,
                    'url': f'/product/{product.id}'
                })
            
            return JsonResponse({
                'status': 'success',
                'products': products_data
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
            
    return JsonResponse({
        'status': 'error',
        'message': 'Chỉ hỗ trợ phương thức POST'
    })

def update_cart_session(request, user_id, cart_id):
    """
    Hàm cập nhật session giỏ hàng khi có thay đổi
    """
    cart_details = get_cart_detail_by_cart_id(cart_id)
    cart_details_serializable = [
        {
            'id': detail.id,
            'product_id': detail.product_id,
            'quantity': detail.quantity,
            'product_image': detail.product.image_url,
            'product_name': detail.product.name,
            'product_price': float(detail.product.price)
        } for detail in cart_details
    ]
    request.session['cart_id'] = cart_id
    request.session['quantity'] = len(cart_details)
    request.session['cart_details'] = cart_details_serializable
    return cart_details_serializable

def increase_cart_item(request, id):
    """
    Tăng số lượng sản phẩm trong giỏ hàng
    """
    if 'user_id' not in request.session:
        return redirect('login')
    
    user_id = request.session['user_id']
    cart = get_or_create_active_cart(user_id)
    
    # Tìm cart detail
    cart_detail = CartDetail.objects.filter(cart_id=cart.id, product_id=id).first()
    
    if cart_detail:
        # Tăng số lượng và lưu lại
        cart_detail.quantity += 1
        cart_detail.save()
        
        # Cập nhật session
        update_cart_session(request, user_id, cart.id)
    else:
        messages.error(request, "Sản phẩm không có trong giỏ hàng")
    
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

def decrease_cart_item(request, id):
    """
    Giảm số lượng sản phẩm trong giỏ hàng, nếu số lượng = 0 thì xóa sản phẩm
    """
    if 'user_id' not in request.session:
        return redirect('login')
    
    user_id = request.session['user_id']
    cart = get_or_create_active_cart(user_id)
    
    # Tìm cart detail
    cart_detail = CartDetail.objects.filter(cart_id=cart.id, product_id=id).first()
    
    if cart_detail:
        # Giảm số lượng
        if cart_detail.quantity > 1:
            cart_detail.quantity -= 1
            cart_detail.save()
        else:
            # Xóa sản phẩm khỏi giỏ hàng nếu số lượng = 1
            cart_detail.delete()
        
        # Cập nhật session
        update_cart_session(request, user_id, cart.id)
    else:
        messages.error(request, "Sản phẩm không có trong giỏ hàng")
    
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

@csrf_exempt
def get_chat_history(request):
    if request.method == 'GET':
        if 'user_id' in request.session:
            # Lấy lịch sử chat từ session
            chat_history = request.session.get('chat_history', [])
            return JsonResponse({
                'status': 'success',
                'chat_history': chat_history
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Người dùng chưa đăng nhập',
                'chat_history': []
            })
    return JsonResponse({
        'status': 'error',
        'message': 'Phương thức không được hỗ trợ'
    })

@csrf_exempt
def save_chat_history(request):
    if request.method == 'POST':
        if 'user_id' in request.session:
            try:
                data = json.loads(request.body)
                chat_history = data.get('chat_history', [])
                
                # Lưu lịch sử chat vào session
                request.session['chat_history'] = chat_history
                request.session.modified = True
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Lịch sử chat đã được lưu'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Người dùng chưa đăng nhập'
            })
    return JsonResponse({
        'status': 'error',
        'message': 'Phương thức không được hỗ trợ'
    })

# AI Agent views
@admin_required
def admin_aiagent(request):
    """Trang quản lý AI Agent trong admin dashboard"""
    from frontend.aiagent.data_processor import DataProcessor
    
    processor = DataProcessor()
    product_count = processor.get_product_count()
    last_update = processor.get_last_update_time()
    custom_data = processor.get_custom_data()
    
    return render(request, 'backend/pages/aiagent/index.html', {
        'title': 'AI Agent Management',
        'product_count': product_count,
        'last_update': last_update,
        'custom_data': custom_data
    })

@admin_required
def admin_aiagent_update_data(request):
    """Cập nhật dữ liệu sản phẩm cho AI Agent"""
    if request.method == 'POST':
        from frontend.aiagent.data_processor import DataProcessor
        
        processor = DataProcessor()
        message, product_count = processor.generate_product_data()
        
        if product_count > 0:
            messages.success(request, message)
        else:
            messages.error(request, message)
    
    return redirect('admin_aiagent')

@admin_required
def admin_aiagent_update_custom_data(request):
    """Cập nhật dữ liệu tùy chỉnh cho AI Agent"""
    if request.method == 'POST':
        from frontend.aiagent.data_processor import DataProcessor
        
        custom_data = request.POST.get('custom_data', '')
        processor = DataProcessor()
        message = processor.save_custom_data(custom_data)
        
        messages.success(request, message)
    
    return redirect('admin_aiagent')

@csrf_exempt
def function_calling(request):
    """API để thực hiện function calling với AI Agent"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            
            if not query:
                return JsonResponse({'error': 'Thiếu thông tin query'}, status=400)
            
            from frontend.aiagent.rag_handler import RAGHandler
            
            handler = RAGHandler()
            response = handler.function_calling(query)
            
            return JsonResponse({'response': response})
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)



