# NeuroScan AI API Reference

## Overview
REST API for MRI Brain Tumor Classification using EfficientNet-B0

## Base URL
```
http://localhost:8000
```

## Authentication
JWT Bearer token required for protected endpoints.
```
Authorization: Bearer <token>
```

---

## Endpoints

### Health Check
```
GET /health
```
Returns API status.

### Authentication

#### Register Doctor
```
POST /api/auth/register
Content-Type: application/json

{
  "email": "doctor@example.com",
  "name": "Dr. John Smith",
  "password": "securepassword123"
}
```
Response:
```json
{
  "doctor_id": "doc_abc123",
  "email": "doctor@example.com",
  "name": "Dr. John Smith"
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "doctor@example.com",
  "password": "securepassword123"
}
```
Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "doctor_id": "doc_abc123",
  "name": "Dr. John Smith"
}
```

### Patients

#### Create Patient
```
POST /api/patients
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Jane Doe",
  "date_of_birth": "1985-03-15",
  "gender": "female",
  "phone": "+1234567890",
  "notes": "Regular checkup"
}
```
Response:
```json
{
  "patient_id": "pat_xyz789",
  "name": "Jane Doe",
  "date_of_birth": "1985-03-15",
  "gender": "female",
  "created_at": "2026-03-26T10:00:00"
}
```

#### List Patients
```
GET /api/patients?skip=0&limit=10
Authorization: Bearer <token>
```

#### Get Patient
```
GET /api/patients/{patient_id}
Authorization: Bearer <token>
```

### MRI Scans

#### Upload Scan
```
POST /api/scans
Authorization: Bearer <token>
Content-Type: multipart/form-data

patient_id: pat_xyz789
scan_date: 2026-03-26
file: [MRI image]
notes: Annual screening
```
Response:
```json
{
  "scan_id": "scan_abc123",
  "patient_id": "pat_xyz789",
  "scan_date": "2026-03-26",
  "tumor_detected": true,
  "confidence_score": 94.5,
  "tumor_type": "Glioma",
  "tumor_location": "Frontal Lobe",
  "analysis_notes": "High confidence detection..."
}
```

#### Get Scans by Patient
```
GET /api/scans/patient/{patient_id}?skip=0&limit=10
Authorization: Bearer <token>
```

### Statistics

#### Get Dashboard Stats
```
GET /api/stats
Authorization: Bearer <token>
```
Response:
```json
{
  "total_patients": 150,
  "total_scans": 320,
  "tumor_detected": 85,
  "no_tumor": 235,
  "by_type": {
    "glioma": 45,
    "meningioma": 25,
    "pituitary": 15
  }
}
```

### Prediction

#### Predict (Standalone)
```
POST /predict
Content-Type: multipart/form-data

file: [MRI image]
```
Response:
```json
{
  "tumor_detected": true,
  "confidence_score": 94.5,
  "tumor_type": "Glioma",
  "tumor_location": "Right Temporal Lobe",
  "analysis_notes": "High confidence tumor detection..."
}
```

---

## Error Responses

```json
{
  "detail": "Error message"
}
```

Common status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error
