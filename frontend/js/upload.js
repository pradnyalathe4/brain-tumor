// Upload handling with drag-drop, progress, and compression

const API_BASE = window.API_CONFIG?.BASE_URL || 'http://localhost:8000';
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const COMPRESS_THRESHOLD = 5 * 1024 * 1024; // 5MB
const MAX_COMPRESS_WIDTH = 1920;
const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/jpg'];
const ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg'];

let selectedFile = null;

// Initialize upload handling when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initUploadHandlers();
});

function initUploadHandlers() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    
    if (!dropZone || !fileInput) return;
    
    // Click to browse
    dropZone.addEventListener('click', () => fileInput.click());
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    // Drag events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-medical-500', 'bg-medical-50');
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-medical-500', 'bg-medical-50');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-medical-500', 'bg-medical-50');
        
        if (e.dataTransfer.files[0]) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });
}

function handleFileSelect(file) {
    // Client-side validation
    if (!ALLOWED_TYPES.includes(file.type)) {
        showToast('Invalid file type. Only PNG and JPEG allowed.', 'error');
        return;
    }
    
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
        showToast('Invalid file extension. Only PNG and JPEG allowed.', 'error');
        return;
    }
    
    if (file.size > MAX_FILE_SIZE) {
        showToast('File too large. Maximum size is 10MB.', 'error');
        return;
    }
    
    // Compress if over threshold (client-side optimization)
    const processFile = async () => {
        let finalFile = file;
        
        if (file.size > COMPRESS_THRESHOLD) {
            showToast('Compressing image...', 'success');
            finalFile = await window.utils.compressImage(file, 5, MAX_COMPRESS_WIDTH);
        }
        
        selectedFile = finalFile;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewImg = document.getElementById('previewImg');
            if (previewImg) {
                previewImg.src = e.target.result;
            }
            const placeholder = document.getElementById('uploadPlaceholder');
            const previewContainer = document.getElementById('previewContainer');
            if (placeholder) placeholder.classList.add('hidden');
            if (previewContainer) previewContainer.classList.remove('hidden');
        };
        reader.readAsDataURL(finalFile);
        
        // Enable analyze button if patient is selected
        updateAnalyzeButton();
    };
    
    processFile().catch(err => {
        showToast('Failed to process image: ' + err.message, 'error');
    });
}

function removeFile(e) {
    if (e) e.stopPropagation();
    selectedFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('previewContainer').classList.add('hidden');
    document.getElementById('uploadPlaceholder').classList.remove('hidden');
    updateAnalyzeButton();
}

function updateAnalyzeButton() {
    const btn = document.getElementById('analyzeBtn');
    const patient = document.getElementById('patientSelect').value;
    btn.disabled = !selectedFile || !patient;
}

function updatePatientSelect() {
    updateAnalyzeButton();
}

// If patient select exists, add listener
if (document.getElementById('patientSelect')) {
    document.getElementById('patientSelect').addEventListener('change', updateAnalyzeButton);
}

async function analyzeScan() {
    const patientId = document.getElementById('patientSelect').value;
    const btn = document.getElementById('analyzeBtn');
    const progressContainer = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    const resultContainer = document.getElementById('resultContainer');
    
    if (!selectedFile) {
        showToast('Please select an MRI image', 'error');
        return;
    }
    
    if (!patientId) {
        showToast('Please select a patient', 'error');
        return;
    }
    
    const doctor = JSON.parse(sessionStorage.getItem('neuroscan_doctor') || '{}');
    if (!doctor.id) {
        showToast('Session expired. Please login again.', 'error');
        window.location.href = 'login.html';
        return;
    }
    
    // Disable button and show progress
    btn.disabled = true;
    btn.textContent = 'Analyzing...';
    progressContainer.classList.remove('hidden');
    progressBar.style.width = '0%';
    progressPercent.textContent = '0%';
    
    try {
        const result = await fetchApiPredict(selectedFile, patientId, doctor.id, (percent) => {
            progressBar.style.width = percent + '%';
            progressPercent.textContent = percent + '%';
        });
        
        // Show result
        displayResult(result);
        showToast('Analysis complete!', 'success');
        
    } catch (error) {
        showToast(error.message, 'error');
        resultContainer.innerHTML = `
            <div class="text-red-600">
                <svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
                <p>Analysis Failed</p>
                <p class="text-sm mt-2">${escapeHtml(error.message)}</p>
            </div>
        `;
    } finally {
        btn.disabled = false;
        btn.textContent = 'Analyze MRI Scan';
        progressContainer.classList.add('hidden');
    }
}

function displayResult(result) {
    const container = document.getElementById('resultContainer');
    const isTumor = result.tumor_detected;
    const confidenceColor = result.confidence_score >= 85 ? 'bg-green-500' : result.confidence_score >= 65 ? 'bg-yellow-500' : 'bg-red-500';
    
    container.innerHTML = `
        <div class="${isTumor ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'} border rounded-xl p-6">
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 rounded-full ${isTumor ? 'bg-red-100' : 'bg-green-100'} flex items-center justify-center">
                        <svg class="w-6 h-6 ${isTumor ? 'text-red-600' : 'text-green-600'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            ${isTumor 
                                ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>'
                                : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>'
                            }
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-xl font-bold ${isTumor ? 'text-red-800' : 'text-green-800'}">
                            ${isTumor ? '⚠️ Tumor Detected' : '✅ No Tumor'}
                        </h3>
                        <p class="text-gray-600">${result.tumor_type || 'N/A'}</p>
                    </div>
                </div>
                <div class="text-right">
                    <div class="text-3xl font-bold text-gray-900">${result.confidence_score}%</div>
                    <p class="text-sm text-gray-500">Confidence</p>
                </div>
            </div>
            
            <!-- Confidence Bar -->
            <div class="mb-4">
                <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full ${confidenceColor} transition-all" style="width: ${result.confidence_score}%"></div>
                </div>
                <div class="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0%</span>
                    <span>50%</span>
                    <span>100%</span>
                </div>
            </div>
            
            <div class="border-t border-gray-200 pt-4">
                <p class="text-sm font-medium text-gray-700 mb-1">Analysis Notes:</p>
                <p class="text-sm text-gray-600">${escapeHtml(result.analysis_notes)}</p>
            </div>
            
            <div class="mt-4 flex gap-4 text-sm text-gray-500">
                <div>
                    <span class="font-medium">Location:</span> ${result.tumor_location || 'N/A'}
                </div>
            </div>
        </div>
    `;
}