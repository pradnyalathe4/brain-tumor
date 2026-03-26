// Utility functions for frontend

// Error mapping for user-friendly messages
const ERROR_MESSAGES = {
    'AUTH_INVALID': 'Wrong email or password',
    'auth_error': 'Authentication failed. Please login again.',
    'invalid_image': 'Invalid image file. Please upload PNG or JPG.',
    'file_too_large': 'File too large. Maximum size is 10MB.',
    'model_not_loaded': 'Analysis service unavailable. Please try again later.',
    'analysis_failed': 'Analysis failed. Please try again.',
    'not_found': 'The requested resource was not found.',
    'email_already_registered': 'This email is already registered.',
    'password_too_short': 'Password must be at least 6 characters.',
    'internal_error': 'Something went wrong. Please try again.'
};

// Format backend error to user-friendly message
function formatError(error) {
    if (!error) return ERROR_MESSAGES.internal_error;
    
    // If error is a string, return as-is
    if (typeof error === 'string') return error;
    
    // If error has code property
    if (error.code && ERROR_MESSAGES[error.code]) {
        return ERROR_MESSAGES[error.code];
    }
    
    // If error has message property
    if (error.message) return error.message;
    
    // If error is from response detail
    if (error.detail) {
        if (typeof error.detail === 'string') return error.detail;
        if (error.detail.message) return error.detail.message;
        if (error.detail.code && ERROR_MESSAGES[error.detail.code]) {
            return ERROR_MESSAGES[error.detail.code];
        }
    }
    
    return ERROR_MESSAGES.internal_error;
}

// Show toast notification
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    const icon = type === 'success' 
        ? '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>'
        : '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>';
    
    toast.className = `px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 animate-fade-in ${
        type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
    }`;
    toast.innerHTML = `${icon}<span>${escapeHtml(message)}</span>`;
    
    container.appendChild(toast);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Compress image if too large
function compressImage(file, maxSizeMB = 5, maxWidth = 1920) {
    return new Promise((resolve, reject) => {
        if (file.size <= maxSizeMB * 1024 * 1024) {
            resolve(file);
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;
                
                // Calculate new dimensions
                if (width > maxWidth) {
                    height = (height * maxWidth) / width;
                    width = maxWidth;
                }
                
                canvas.width = width;
                canvas.height = height;
                
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                
                // Try progressively lower quality until under max size
                const compress = (quality) => {
                    return new Promise((res) => {
                        canvas.toBlob((blob) => {
                            res(blob);
                        }, 'image/jpeg', quality);
                    });
                };
                
                const tryCompress = async () => {
                    let quality = 0.9;
                    let blob = await compress(quality);
                    
                    while (blob.size > maxSizeMB * 1024 * 1024 && quality > 0.3) {
                        quality -= 0.1;
                        blob = await compress(quality);
                    }
                    
                    if (blob.size > maxSizeMB * 1024 * 1024) {
                        // Still too large, return original with warning
                        resolve(file);
                    } else {
                        resolve(new File([blob], file.name.replace(/\.[^.]+$/, '.jpg'), { type: 'image/jpeg' }));
                    }
                };
                
                tryCompress();
            };
            img.onerror = () => reject(new Error('Failed to load image'));
            img.src = e.target.result;
        };
        reader.onerror = () => reject(new Error('Failed to read file'));
        reader.readAsDataURL(file);
    });
}

// Sleep utility
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Retry with exponential backoff
async function retryWithBackoff(fn, maxAttempts = 3, initialDelay = 1000) {
    let lastError;
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;
            
            // Don't retry on client errors (4xx)
            if (error.status && error.status < 500) {
                throw error;
            }
            
            if (attempt < maxAttempts) {
                const delay = Math.min(initialDelay * Math.pow(2, attempt - 1), 10000);
                await sleep(delay);
            }
        }
    }
    
    throw lastError;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export utilities
window.utils = {
    formatError,
    showToast,
    compressImage,
    retryWithBackoff,
    escapeHtml,
    formatDate,
    debounce,
    ERROR_MESSAGES
};