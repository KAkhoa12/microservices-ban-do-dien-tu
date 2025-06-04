/**
 * Cart Update JavaScript
 * Handles real-time cart updates in header
 */

// Function to update cart display in header
function updateCartDisplay(cartData) {
    console.log('Updating cart display with data:', cartData);

    // Update cart quantity in header
    const cartQuantityElement = document.querySelector('.header-ctn .qty');
    if (cartQuantityElement) {
        cartQuantityElement.textContent = cartData.cart_quantity || 0;
        console.log('Updated cart quantity to:', cartData.cart_quantity || 0);
    }

    // Update cart dropdown
    const cartDropdown = document.querySelector('.cart-dropdown');
    if (cartDropdown) {
        updateCartDropdown(cartDropdown, cartData);
    }
}

// Function to update cart dropdown content
function updateCartDropdown(dropdown, cartData) {
    const cartItems = cartData.cart_details || [];
    const cartQuantity = cartData.cart_quantity || 0;
    const cartTotal = cartData.cart_total || 0;

    console.log('Updating cart dropdown with items:', cartItems);

    if (cartQuantity === 0 || cartItems.length === 0) {
        // Empty cart
        dropdown.innerHTML = `
            <div>
                <h5>Không có sản phẩm nào được thêm vào</h5>
            </div>
            <div class="cart-summary">
                <small>0 Item(s) selected</small>
                <h5>SUBTOTAL: 0 vnđ</h5>
            </div>
        `;
    } else {
        // Cart with items
        const cartItemsHtml = cartItems.map(item => `
            <div class="product-widget">
                <div class="product-img">
                    <img src="${item.product?.image_url || '/static/img/no-image.png'}" alt="">
                </div>
                <div class="product-body">
                    <h3 class="product-name">
                        <a href="/product/${item.product?.id || '#'}">${item.product?.name || 'Unknown Product'}</a>
                    </h3>
                    <h4 class="product-price">
                        <span class="qty">${item.quantity || 1}x</span>
                        ${formatPrice(item.product?.price || 0)}
                    </h4>
                </div>
                <a href="/remove-from-cart/${item.product?.id || 0}/" class="delete" onclick="removeFromCartAjax(${item.product?.id || 0}); return false;">
                    <i class="fa fa-close"></i>
                </a>
            </div>
        `).join('');

        dropdown.innerHTML = `
            <div class="cart-list">
                ${cartItemsHtml}
            </div>
            <div class="cart-summary">
                <small>${cartQuantity} Item(s) selected</small>
                <h5>SUBTOTAL: ${formatPrice(cartTotal)}</h5>
            </div>
            <div class="cart-btns" style="width: 100%;">
                <a href="/cart/" style="width: 100%;">View Cart</a>
            </div>
        `;
    }
}

// Function to format price
function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(price || 0);
}

// Function to fetch cart data from API
async function fetchCartData() {
    try {
        console.log('Fetching cart data...');
        const response = await fetch('/api/cart-data/', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Cart data response:', data);

        if (data.status === 'success') {
            updateCartDisplay(data.data);
            return data.data;
        } else {
            console.error('Error fetching cart data:', data.message);
            return null;
        }
    } catch (error) {
        console.error('Error fetching cart data:', error);
        return null;
    }
}

// Function to refresh cart data
function refreshCartData() {
    console.log('Refreshing cart data...');
    fetchCartData();
}

// Function to handle add to cart with AJAX
async function addToCartAjax(productId) {
    try {
        console.log('Adding product to cart:', productId);
        const response = await fetch(`/add-to-cart/${productId}/`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            console.log('Product added successfully');
            // Refresh cart data after successful add
            setTimeout(refreshCartData, 500); // Small delay to ensure backend is updated

            // Show success message
            showNotification('Đã thêm sản phẩm vào giỏ hàng!', 'success');
        } else {
            console.error('Failed to add product');
            showNotification('Có lỗi xảy ra khi thêm sản phẩm!', 'error');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('Có lỗi xảy ra khi thêm sản phẩm!', 'error');
    }
}

// Function to remove from cart with AJAX
async function removeFromCartAjax(productId) {
    try {
        console.log('Removing product from cart:', productId);
        const response = await fetch(`/remove-from-cart/${productId}/`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            console.log('Product removed successfully');
            // Refresh cart data after successful removal
            setTimeout(refreshCartData, 500);
            showNotification('Đã xóa sản phẩm khỏi giỏ hàng!', 'success');
        } else {
            console.error('Failed to remove product');
            showNotification('Có lỗi xảy ra khi xóa sản phẩm!', 'error');
        }
    } catch (error) {
        console.error('Error removing from cart:', error);
        showNotification('Có lỗi xảy ra khi xóa sản phẩm!', 'error');
    }
}

// Function to show notifications
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.cart-notification');
    existingNotifications.forEach(n => n.remove());

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `cart-notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        border-radius: 4px;
        z-index: 10000;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        font-size: 14px;
        max-width: 300px;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Remove notification after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Initialize cart data when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Cart update script loaded');

    // Fetch initial cart data
    fetchCartData();

    // Override existing add to cart buttons to use AJAX
    // Handle both <a> tags with href and <button> tags with onclick
    const addToCartLinks = document.querySelectorAll('a[href*="/add-to-cart/"]');
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');

    console.log('Found add to cart links:', addToCartLinks.length);
    console.log('Found add to cart buttons:', addToCartButtons.length);

    // Handle <a> tags with href
    addToCartLinks.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            const match = href.match(/\/add-to-cart\/(\d+)\//);
            if (match) {
                const productId = match[1];
                console.log('Add to cart link clicked for product:', productId);
                addToCartAjax(productId);
            }
        });
    });

    // Handle <button> tags with onclick or data attributes
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Try to get product ID from onclick attribute
            const onclick = this.getAttribute('onclick');
            if (onclick) {
                const match = onclick.match(/add-to-cart\/(\d+)\//);
                if (match) {
                    const productId = match[1];
                    console.log('Add to cart button clicked for product:', productId);
                    addToCartAjax(productId);
                    return;
                }
            }

            // Try to get product ID from data attribute
            const productId = this.getAttribute('data-product-id');
            if (productId) {
                console.log('Add to cart button clicked for product (data-id):', productId);
                addToCartAjax(productId);
                return;
            }

            // Try to find product ID from parent elements
            const productElement = this.closest('[data-product-id]');
            if (productElement) {
                const productId = productElement.getAttribute('data-product-id');
                console.log('Add to cart button clicked for product (parent):', productId);
                addToCartAjax(productId);
                return;
            }

            console.log('Could not find product ID for add to cart button');
        });
    });
});

// Export functions for global use
window.refreshCartData = refreshCartData;
window.addToCartAjax = addToCartAjax;
window.removeFromCartAjax = removeFromCartAjax;
