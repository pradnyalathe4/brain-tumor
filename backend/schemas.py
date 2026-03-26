from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Auth Schemas
class DoctorResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    created_at: Optional[datetime] = None

class DoctorRegister(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)

class DoctorLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    doctor: DoctorResponse

# Patient Schemas
class PatientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: Optional[str] = None
    gender: Optional[Gender] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    medical_history: Optional[str] = Field(None, max_length=2000)

class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    date_of_birth: Optional[str] = None
    gender: Optional[Gender] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    medical_history: Optional[str] = Field(None, max_length=2000)

class PatientResponse(BaseModel):
    id: str
    doctor_id: str
    name: str
    date_of_birth: Optional[str]
    gender: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    medical_history: Optional[str]
    created_at: datetime

# Scan Schemas
class ScanResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    scan_date: datetime
    image_path: str
    analysis_status: str
    tumor_detected: Optional[bool]
    confidence_score: Optional[float]
    tumor_type: Optional[str]
    tumor_location: Optional[str]
    analysis_notes: Optional[str]
    created_at: datetime
    patient_name: Optional[str] = None

class ScanDetailResponse(ScanResponse):
    image_url: Optional[str] = None

# Stats Schema
class StatsResponse(BaseModel):
    total_patients: int
    total_scans: int
    tumors_detected: int
    tumor_types: dict
    monthly_scans: dict

# Analysis Schemas
class PredictionRequest(BaseModel):
    patient_id: str
    doctor_id: str

class PredictionResponse(BaseModel):
    tumor_detected: bool
    confidence_score: float
    tumor_type: Optional[str]
    tumor_location: Optional[str]
    analysis_notes: str

# Error Schemas
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail