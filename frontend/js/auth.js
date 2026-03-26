// Auth utilities using new config

const API_BASE = window.API_CONFIG?.BASE_URL || 'http://localhost:8000';

async function fetchAuthLogin(email, password) {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    
    const data = await response.json().catch(() => ({}));
    
    if (!response.ok) {
        const message = data.detail?.message || data.detail || 'Login failed';
        throw new Error(message);
    }
    
    return data;
}

async function fetchAuthRegister(name, email, password) {
    const response = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
    });
    
    const data = await response.json().catch(() => ({}));
    
    if (!response.ok) {
        const message = data.detail?.message || data.detail || 'Registration failed';
        throw new Error(message);
    }
    
    return data;
}

function logout() {
    sessionStorage.removeItem('neuroscan_token');
    sessionStorage.removeItem('neuroscan_doctor');
    window.location.href = 'login.html';
}

function getToken() {
    return sessionStorage.getItem('neuroscan_token');
}

function isAuthenticated() {
    return !!getToken();
}

// Initialize error messages from utils
if (window.utils) {
    window.utils.ERROR_MESSAGES = {
        ...window.utils.ERROR_MESSAGES,
        'AUTH_INVALID': 'Wrong email or password',
        'auth_error': 'Authentication failed. Please login again.',
        'email_already_registered': 'This email is already registered.',
        'password_too_short': 'Password must be at least 6 characters.'
    };
}