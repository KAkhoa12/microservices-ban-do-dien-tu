// Login form handling with localStorage
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Check if user is already logged in
    checkExistingAuth();
});

async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.textContent = 'Đang đăng nhập...';
    
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Save tokens to localStorage
            const { access_token, refresh_token, expires_in, refresh_expires_in } = data.data;
            
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            localStorage.setItem('token_expires_at', Date.now() + (expires_in * 1000));
            localStorage.setItem('refresh_expires_at', Date.now() + (refresh_expires_in * 1000));
            
            // Get user info and save to localStorage
            await getUserInfo(access_token);
            
            // Show success message
            showMessage('Đăng nhập thành công!', 'success');
            
            // Redirect after short delay
            setTimeout(() => {
                const nextUrl = new URLSearchParams(window.location.search).get('next');
                window.location.href = nextUrl || '/';
            }, 1000);
            
        } else {
            showMessage(data.message || 'Đăng nhập thất bại', 'error');
        }
        
    } catch (error) {
        console.error('Login error:', error);
        showMessage('Có lỗi xảy ra khi đăng nhập', 'error');
    } finally {
        // Reset button state
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    }
}

async function getUserInfo(token) {
    try {
        const response = await fetch('/api/user/me', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            localStorage.setItem('user_data', JSON.stringify(data.data));
            return data.data;
        } else {
            throw new Error(data.message || 'Failed to get user info');
        }
        
    } catch (error) {
        console.error('Error getting user info:', error);
        // Clear tokens if user info fetch fails
        clearAuthData();
        throw error;
    }
}

function checkExistingAuth() {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');
    
    if (token && userData) {
        // Check if token is still valid
        const expiresAt = localStorage.getItem('token_expires_at');
        if (expiresAt && Date.now() < parseInt(expiresAt)) {
            // User is already logged in, redirect to home or next page
            const nextUrl = new URLSearchParams(window.location.search).get('next');
            window.location.href = nextUrl || '/';
        } else {
            // Token expired, try to refresh
            tryRefreshToken();
        }
    }
}

async function tryRefreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    const refreshExpiresAt = localStorage.getItem('refresh_expires_at');
    
    if (!refreshToken || Date.now() >= parseInt(refreshExpiresAt)) {
        // Refresh token expired, clear auth data
        clearAuthData();
        return;
    }
    
    try {
        const response = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                refresh_token: refreshToken
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const { access_token, expires_in } = data.data;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('token_expires_at', Date.now() + (expires_in * 1000));
            
            // Get updated user info
            await getUserInfo(access_token);
            
            // Redirect to home or next page
            const nextUrl = new URLSearchParams(window.location.search).get('next');
            window.location.href = nextUrl || '/';
        } else {
            clearAuthData();
        }
        
    } catch (error) {
        console.error('Token refresh error:', error);
        clearAuthData();
    }
}

function clearAuthData() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('token_expires_at');
    localStorage.removeItem('refresh_expires_at');
}

function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.auth-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `auth-message alert alert-${type === 'success' ? 'success' : 'danger'}`;
    messageDiv.textContent = message;
    
    // Insert message at the top of the form
    const form = document.getElementById('login-form');
    if (form) {
        form.insertBefore(messageDiv, form.firstChild);
        
        // Auto-remove message after 5 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
}

// Utility functions for other pages
window.AuthUtils = {
    getToken: () => localStorage.getItem('access_token'),
    getUserData: () => {
        const userData = localStorage.getItem('user_data');
        return userData ? JSON.parse(userData) : null;
    },
    isAuthenticated: () => {
        const token = localStorage.getItem('access_token');
        const expiresAt = localStorage.getItem('token_expires_at');
        return token && expiresAt && Date.now() < parseInt(expiresAt);
    },
    isAdmin: () => {
        const userData = window.AuthUtils.getUserData();
        return userData && userData.user_role === 'admin';
    },
    logout: () => {
        clearAuthData();
        window.location.href = '/';
    },
    requireAuth: () => {
        if (!window.AuthUtils.isAuthenticated()) {
            window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
            return false;
        }
        return true;
    },
    requireAdmin: () => {
        if (!window.AuthUtils.isAuthenticated()) {
            window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
            return false;
        }
        if (!window.AuthUtils.isAdmin()) {
            alert('Bạn không có quyền truy cập trang này');
            window.location.href = '/';
            return false;
        }
        return true;
    }
};
