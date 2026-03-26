// API wrapper with authorization, retry logic, and error handling

const API_BASE = window.API_CONFIG?.BASE_URL || 'http://localhost:8000';
const TIMEOUT = window.API_CONFIG?.TIMEOUTS?.DEFAULT || 30000;
const UPLOAD_TIMEOUT = window.API_CONFIG?.TIMEOUTS?.UPLOAD || 120000;

async function apiRequest(endpoint, options = {}) {
    const token = sessionStorage.getItem('neuroscan_token');
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const makeRequest = async () => {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), options.timeout || TIMEOUT);
        
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                ...options,
                headers,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            // Handle 401
            if (response.status === 401) {
                sessionStorage.removeItem('neuroscan_token');
                sessionStorage.removeItem('neuroscan_doctor');
                window.location.href = 'login.html';
                throw { status: 401, message: 'Session expired' };
            }
            
            // Parse response
            let data;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                data = await response.json().catch(() => ({}));
            }
            
            if (!response.ok) {
                const message = data?.detail?.message || data?.detail || `Request failed (${response.status})`;
                throw { status: response.status, message };
            }
            
            return data;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw { status: 0, message: 'Request timeout' };
            }
            throw error;
        }
    };
    
    // Retry logic for 5xx errors
    const maxRetries = window.API_CONFIG?.RETRY?.MAX_ATTEMPTS || 3;
    const initialDelay = window.API_CONFIG?.RETRY?.INITIAL_DELAY || 1000;
    
    let lastError;
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await makeRequest();
        } catch (error) {
            lastError = error;
            
            // Don't retry on client errors (4xx except 401)
            if (error.status && error.status >= 400 && error.status < 500) {
                throw error;
            }
            
            // Don't retry on abort/timeout
            if (error.status === 0) {
                throw error;
            }
            
            if (attempt < maxRetries) {
                const delay = Math.min(initialDelay * Math.pow(2, attempt - 1), 10000);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    
    throw lastError;
}

// Auth endpoints
async function fetchApiMe() {
    return apiRequest('/api/auth/me');
}

// Patients endpoints
async function fetchApiPatients() {
    return apiRequest('/api/patients');
}

async function fetchApiCreatePatient(data) {
    return apiRequest('/api/patients', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

// Scans endpoints
async function fetchApiScans() {
    return apiRequest('/api/scans');
}

// Stats endpoint
async function fetchApiStats() {
    return apiRequest('/api/stats');
}

// Prediction endpoint with progress tracking
async function fetchApiPredict(file, patientId, doctorId, onProgress) {
    const token = sessionStorage.getItem('neuroscan_token');
    
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        
        // Progress handler
        if (onProgress) {
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    onProgress(percent);
                }
            });
        }
        
        // Load handler
        xhr.addEventListener('load', () => {
            if (xhr.status === 401) {
                sessionStorage.removeItem('neuroscan_token');
                sessionStorage.removeItem('neuroscan_doctor');
                window.location.href = 'login.html';
                reject(new Error('Session expired'));
                return;
            }
            
            if (xhr.status >= 400) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    const message = data?.detail?.message || data?.detail || 'Analysis failed';
                    reject(new Error(message));
                } catch {
                    reject(new Error('Analysis failed'));
                }
                return;
            }
            
            try {
                resolve(JSON.parse(xhr.responseText));
            } catch {
                reject(new Error('Invalid response'));
            }
        });
        
        // Error handler
        xhr.addEventListener('error', () => {
            reject(new Error('Network error'));
        });
        
        // Abort handler
        xhr.addEventListener('abort', () => {
            reject(new Error('Request cancelled'));
        });
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('patient_id', patientId);
        formData.append('doctor_id', doctorId);
        
        xhr.open('POST', `${API_BASE}/predict`);
        if (token) {
            xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        }
        
        // Set longer timeout for uploads
        xhr.timeout = UPLOAD_TIMEOUT;
        
        xhr.send(formData);
    });
}

// Export API object for convenience
window.api = {
    login: fetchAuthLogin,
    register: fetchAuthRegister,
    me: fetchApiMe,
    patients: {
        list: fetchApiPatients,
        create: fetchApiCreatePatient
    },
    scans: {
        list: fetchApiScans
    },
    stats: fetchApiStats,
    predict: fetchApiPredict
};