// API Configuration
// In production, these would be injected via environment variables

const API_CONFIG = {
    // Get base URL from meta tag or default to localhost
    BASE_URL: (() => {
        const meta = document.querySelector('meta[name="api-base-url"]');
        return meta ? meta.getAttribute('content') : 'http://localhost:8000';
    })(),
    
    // Endpoints
    ENDPOINTS: {
        LOGIN: '/api/auth/login',
        REGISTER: '/api/auth/register',
        ME: '/api/auth/me',
        PATIENTS: '/api/patients',
        SCANS: '/api/scans',
        STATS: '/api/stats',
        PREDICT: '/predict'
    },
    
    // Timeouts (ms)
    TIMEOUTS: {
        DEFAULT: 30000,
        UPLOAD: 120000
    },
    
    // Retry configuration
    RETRY: {
        MAX_ATTEMPTS: 3,
        INITIAL_DELAY: 1000,
        MAX_DELAY: 10000
    }
};

// Export for use in other modules
window.API_CONFIG = API_CONFIG;