# MRI Brain Tumor Classification - NeuroScan AI

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115-red?style=flat-square&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/TensorFlow-2.18-orange?style=flat-square&logo=tensorflow" alt="TensorFlow">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Status-Research-yellow?style=flat-square" alt="Status">
</p>

---

## 🎯 Project Overview

**NeuroScan AI** is a deep learning-based medical imaging system for automated brain tumor detection and classification from MRI scans.

### Key Capabilities

- **4-Class Tumor Classification**: Glioma, Meningioma, Pituitary Tumor, No Tumor
- **Transfer Learning**: EfficientNet-B0 architecture pre-trained on ImageNet
- **REST API**: FastAPI backend with JWT authentication
- **Vanilla JS Frontend**: Responsive, accessible UI without build dependencies
- **SQLite Database**: Local storage for patients and scan history

### Use Cases

- Research and educational purposes
- Clinical decision support (must be validated by radiologists)
- Medical imaging analysis workflows
- AI model benchmarking

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run with Docker
docker build -t neuroscan-ai .
docker run -p 8000:8000 neuroscan-ai
```

### Option 2: Local Development

```bash
# Clone repository
git clone https://github.com/your-org/mri-brain-tumor-classification.git
cd mri-brain-tumor-classification-efficientnet

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# OR (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run server
cd backend
python main.py
```

### Access the Application

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Demo Login**: `doctor@demo.com` / `demo123`

---

## 🔐 Security Practices

### Authentication & Authorization

- **JWT Tokens**: HS256 algorithm with configurable expiration
- **Password Hashing**: bcrypt via passlib
- **Session Storage**: sessionStorage (not localStorage) for token
- **Token Expiration**: 24-hour default (configurable)

### Input Validation

- **File Validation**: Magic bytes check (not just extension)
- **Size Limits**: 10MB max for uploads
- **Type Restrictions**: PNG, JPEG only
- **SQL Injection**: Parameterized queries via SQLModel

### API Security

```env
# .env configuration
JWT_SECRET=your-secure-random-string
CORS_ORIGINS=http://localhost:3000
MAX_FILE_SIZE_MB=10
```

---

## 📡 API Reference

### Base URL
```
http://localhost:8000
```

### Authentication

#### Register Doctor
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Smith",
    "email": "smith@hospital.com",
    "password": "securepassword123"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@demo.com",
    "password": "demo123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "doctor": {
    "id": "doc-123",
    "email": "doctor@demo.com",
    "name": "Demo Doctor"
  }
}
```

### Endpoints (Requires Authorization)

#### Get Current User
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <token>"
```

#### List Patients
```bash
curl -X GET http://localhost:8000/api/patients \
  -H "Authorization: Bearer <token>"
```

#### Create Patient
```bash
curl -X POST http://localhost:8000/api/patients \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "date_of_birth": "1985-03-15",
    "gender": "male",
    "contact_email": "john@example.com"
  }'
```

#### List Scans
```bash
curl -X GET http://localhost:8000/api/scans \
  -H "Authorization: Bearer <token>"
```

#### Get Stats
```bash
curl -X GET http://localhost:8000/api/stats \
  -H "Authorization: Bearer <token>"
```

### Prediction Endpoint

#### Upload MRI & Get Prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer <token>" \
  -F "file=@mri_scan.png" \
  -F "patient_id=<patient-id>" \
  -F "doctor_id=<doctor-id>"
```

**Response:**
```json
{
  "tumor_detected": true,
  "confidence_score": 94.52,
  "tumor_type": "Glioma",
  "tumor_location": "Frontal Lobe",
  "analysis_notes": "Glioma detected with high confidence. Findings strongly suggest pathology. Clinical correlation advised."
}
```

### Error Response Format

```json
{
  "error": {
    "code": "auth_invalid",
    "message": "Wrong email or password"
  }
}
```

---

## 🧠 Model Details

### Architecture: EfficientNet-B0

| Property | Value |
|----------|-------|
| Input Size | 224 × 224 × 3 |
| Parameters | ~5.3M |
| Training | Transfer learning from ImageNet |
| Framework | TensorFlow 2.18 |

### Tumor Classes

1. **Glioma**: tumors arising from glial cells
2. **Meningioma**: tumors of the meninges
3. **Pituitary**: tumors of the pituitary gland
4. **No Tumor**: healthy brain scan

### Dataset

- Source: Public MRI datasets (e.g., Brain Tumor Segmentation Challenge)
- Preprocessing: Resize to 224×224, normalize to ImageNet stats
- Augmentation: Random horizontal flip, rotation (±15°), brightness adjustment

### Expected Accuracy

> **Note**: Model accuracy varies based on dataset and preprocessing. Always validate with clinical evaluation.

---

## ♿ Accessibility & Compliance

### Accessibility Features

- WCAG 2.1 AA compliant color contrast
- Keyboard navigation support
- ARIA labels on interactive elements
- Screen reader compatible

### HIPAA Disclaimer

> ⚠️ **IMPORTANT**: This software is NOT HIPAA certified. Before using with real patient data:
> - Implement proper data anonymization
> - Add audit logging
> - Enable encryption at rest
> - Consult compliance experts

### Medical Device Disclaimer

> ⚠️ **FDA Notice**: This software is **NOT** FDA-cleared as a medical device. 
> 
> - For research/educational use only
> - Always correlate AI predictions with clinical evaluation
> - Final diagnosis must be made by qualified healthcare professional
> - See [DISCLAIMER.md](DISCLAIMER.md) for full legal information

---

## 🛠️ Development

### Running Tests

```bash
# Backend tests
pip install pytest pytest-asyncio pytest-cov
pytest --cov=backend

# Frontend tests
cd frontend
npm install
npm test
```

### Code Quality

```bash
# Format code
black backend/
isort backend/

# Lint
ruff check backend/
```

---

## 📁 Project Structure

```
mri-brain-tumor-classification-efficientnet/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── security.py          # Auth utilities
│   ├── database.py         # SQLModel setup
│   ├── routers/            # API endpoints
│   ├── models/             # ML model
│   └── requirements.txt
├── frontend/
│   ├── index.html          # Entry point
│   ├── login.html          # Auth page
│   ├── dashboard.html     # Main UI
│   ├── predict.html        # Upload page
│   ├── js/                 # Vanilla JS
│   └── css/                # Styles
├── tests/                  # Backend tests
├── frontend/tests/         # Frontend tests
├── pyproject.toml         # Project config
├── README.md
├── API.md                  # API documentation
├── CONTRIBUTING.md         # Contribution guide
└── DISCLAIMER.md           # Legal disclaimer
```

---

## 📄 License & Support

- **License**: MIT (see LICENSE file)
- **Issues**: Open a GitHub issue for bugs/features
- **Discussions**: Use GitHub Discussions

---

<p align="center">Built with ❤️ for medical AI research</p>