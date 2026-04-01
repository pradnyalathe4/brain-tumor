let selectedFile = null;

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const previewContainer = document.getElementById("preview-container");
const imagePreview = document.getElementById("image-preview");
const analyzeBtn = document.getElementById("analyze-btn");
const patientSelect = document.getElementById("patient-select");

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
});

fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) handleFile(file);
});

function handleFile(file) {
    if (!file.type.startsWith("image/")) {
        showAlert("Please select an image file", "error");
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        showAlert("File too large. Max size is 10MB", "error");
        return;
    }
    
    selectedFile = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        dropZone.style.display = "none";
        previewContainer.style.display = "block";
        analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

function clearPreview() {
    selectedFile = null;
    fileInput.value = "";
    imagePreview.src = "";
    dropZone.style.display = "block";
    previewContainer.style.display = "none";
    analyzeBtn.disabled = true;
    hideResult();
}

analyzeBtn.addEventListener("click", async () => {
    if (!selectedFile) return;
    
    const loadingOverlay = document.getElementById("loading-overlay");
    loadingOverlay.style.display = "flex";
    
    const formData = new FormData();
    formData.append("file", selectedFile);
    
    const patientId = patientSelect.value;
    if (patientId) {
        formData.append("patient_id", patientId);
    }
    
    try {
        const res = await apiFetch("/api/predict", {
            method: "POST",
            body: formData
        });
        
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Prediction failed");
        }
        
        const result = await res.json();
        showResult(result);
        
        if (patientId) {
            showAlert("Scan saved to patient record", "success");
        }
    } catch (err) {
        showAlert(err.message, "error");
    } finally {
        loadingOverlay.style.display = "none";
    }
});

function showResult(result) {
    const section = document.getElementById("result-section");
    section.style.display = "block";
    
    const badge = document.getElementById("tumor-badge");
    badge.textContent = result.tumor_type;
    
    if (result.is_inconclusive) {
        badge.className = "badge badge-large tag-inconclusive";
    } else {
        badge.className = "badge badge-large tag-" + result.tumor_type.toLowerCase().replace(" ", "-");
    }
    
    document.getElementById("confidence-display").textContent = result.confidence_score + "%";
    document.getElementById("location-display").textContent = result.tumor_location;
    document.getElementById("notes-display").textContent = result.analysis_notes;
    
    const bar = document.getElementById("confidence-bar");
    bar.style.width = "0%";
    setTimeout(() => {
        bar.style.width = result.confidence_score + "%";
    }, 100);
    
    const probs = result.all_probabilities || {};
    const container = document.getElementById("probability-bars");
    container.innerHTML = Object.entries(probs).map(([type, prob]) => `
        <div class="probability-bar">
            <span class="prob-label">${type}</span>
            <div class="prob-track">
                <div class="prob-fill tag-${type.toLowerCase().replace(" ", "-")}" style="width: ${prob}%"></div>
            </div>
            <span class="prob-value">${prob}%</span>
        </div>
    `).join("");
    
    document.getElementById("view-scan-link").href = "/scans/" + result.scan_id;
    
    section.scrollIntoView({ behavior: "smooth" });
}

function hideResult() {
    document.getElementById("result-section").style.display = "none";
}

function resetPredict() {
    clearPreview();
    window.history.replaceState({}, "", "/predict");
}

document.addEventListener("DOMContentLoaded", () => {
    loadPatientDropdown();
});

async function loadPatientDropdown() {
    try {
        const res = await apiFetch("/api/patients");
        if (!res) return;
        const data = await res.json();
        
        patientSelect.innerHTML = '<option value="">-- No patient --</option>' +
            data.map(p => `<option value="${p.id}">${p.name}</option>`).join("");
        
        const params = new URLSearchParams(window.location.search);
        const patientId = params.get("patient_id");
        if (patientId) {
            patientSelect.value = patientId;
        }
    } catch (err) {}
}
