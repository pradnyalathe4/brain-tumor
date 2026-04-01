import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from config import settings
from database import get_session
from models.db_models import Scan, Doctor, Patient
from models.ml_model import predict as ml_predict
from security import get_current_doctor

router = APIRouter()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_MAGIC = {
    b"\x89PNG": "png",
    b"\xff\xd8\xff": "jpg"
}

class PredictResponse(BaseModel):
    scan_id: str
    tumor_detected: bool
    tumor_type: str
    confidence_score: float
    tumor_location: str
    analysis_notes: str
    all_probabilities: dict
    patient_id: str
    patient_name: Optional[str] = None
    is_inconclusive: bool = False
    
    class Config:
        extra = "allow"

def validate_image(file_bytes: bytes) -> bool:
    return any(file_bytes.startswith(magic) for magic in ALLOWED_MAGIC)

@router.post("/predict")
async def predict(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    doctor: Doctor = Depends(get_current_doctor)
):
    # Read file content
    content = await file.read()
    
    # Check file size
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size is {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    # Check magic bytes
    if not validate_image(content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PNG and JPEG allowed"
        )
    
    # Validate patient if provided
    patient = None
    if patient_id:
        stmt = select(Patient).where(Patient.id == patient_id, Patient.doctor_id == doctor.id)
        patient = session.exec(stmt).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
    
    # Save file
    ext = ALLOWED_MAGIC.get(bytes(content[:3]), "jpg")
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Run prediction
    result = ml_predict(content)
    
    # Force include is_inconclusive in response
    if "is_inconclusive" not in result:
        result["is_inconclusive"] = False
    
    # Save scan to database
    scan = Scan(
        patient_id=patient_id or "",
        doctor_id=doctor.id,
        image_path=filepath,
        tumor_detected=result["tumor_detected"],
        tumor_type=result["tumor_type"],
        confidence_score=result["confidence_score"],
        tumor_location=result["tumor_location"],
        analysis_notes=result["analysis_notes"]
    )
    session.add(scan)
    session.commit()
    session.refresh(scan)
    
    # Run prediction
    result = ml_predict(content)
    
    print(f"ML predict result keys: {result.keys()}")
    print(f"is_inconclusive value: {result.get('is_inconclusive')}")
    
    response_data = {
        "scan_id": scan.id,
        "tumor_detected": result["tumor_detected"],
        "tumor_type": result["tumor_type"],
        "confidence_score": result["confidence_score"],
        "tumor_location": result["tumor_location"],
        "analysis_notes": result["analysis_notes"],
        "all_probabilities": result["all_probabilities"],
        "patient_id": patient_id or "",
        "patient_name": patient.name if patient else None,
        "is_inconclusive": bool(result.get("is_inconclusive", False))
    }
    
    print(f"Response data: {response_data}")
    
    return response_data
