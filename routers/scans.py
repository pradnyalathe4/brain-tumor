from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from database import get_session
from models.db_models import Scan, Doctor
from security import get_current_doctor

router = APIRouter()

class ScanResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    image_path: str
    tumor_detected: bool
    tumor_type: str
    confidence_score: float
    tumor_location: Optional[str]
    analysis_notes: str
    created_at: str
    patient_name: Optional[str] = None

class StatsResponse(BaseModel):
    total_patients: int
    total_scans: int
    tumor_detected_count: int
    no_tumor_count: int
    tumor_type_breakdown: dict
    recent_scans: List[ScanResponse]

@router.get("", response_model=List[ScanResponse])
def list_scans(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    doctor: Doctor = Depends(get_current_doctor)
):
    statement = select(Scan).where(Scan.doctor_id == doctor.id).order_by(Scan.created_at.desc()).offset(skip).limit(limit)
    scans = session.exec(statement).all()
    
    result = []
    for s in scans:
        result.append(ScanResponse(
            id=s.id,
            patient_id=s.patient_id,
            doctor_id=s.doctor_id,
            image_path=s.image_path,
            tumor_detected=s.tumor_detected,
            tumor_type=s.tumor_type,
            confidence_score=s.confidence_score,
            tumor_location=s.tumor_location,
            analysis_notes=s.analysis_notes,
            created_at=s.created_at.isoformat(),
            patient_name=s.patient.name if s.patient else None
        ))
    return result

@router.get("/stats", response_model=StatsResponse)
def get_stats(
    session: Session = Depends(get_session),
    doctor: Doctor = Depends(get_current_doctor)
):
    from models.db_models import Patient
    
    pat_stmt = select(Patient).where(Patient.doctor_id == doctor.id)
    patients = session.exec(pat_stmt).all()
    total_patients = len(patients)
    
    scan_stmt = select(Scan).where(Scan.doctor_id == doctor.id)
    scans = session.exec(scan_stmt).all()
    total_scans = len(scans)
    
    tumor_detected_count = sum(1 for s in scans if s.tumor_detected)
    no_tumor_count = sum(1 for s in scans if not s.tumor_detected)
    
    tumor_type_breakdown = {"Glioma": 0, "Meningioma": 0, "Pituitary": 0, "No Tumor": 0}
    for s in scans:
        if s.tumor_type in tumor_type_breakdown:
            tumor_type_breakdown[s.tumor_type] += 1
    
    recent_stmt = select(Scan).where(Scan.doctor_id == doctor.id).order_by(Scan.created_at.desc()).limit(5)
    recent = session.exec(recent_stmt).all()
    recent_scans = []
    for s in recent:
        recent_scans.append(ScanResponse(
            id=s.id,
            patient_id=s.patient_id,
            doctor_id=s.doctor_id,
            image_path=s.image_path,
            tumor_detected=s.tumor_detected,
            tumor_type=s.tumor_type,
            confidence_score=s.confidence_score,
            tumor_location=s.tumor_location,
            analysis_notes=s.analysis_notes,
            created_at=s.created_at.isoformat(),
            patient_name=s.patient.name if s.patient else None
        ))
    
    return StatsResponse(
        total_patients=total_patients,
        total_scans=total_scans,
        tumor_detected_count=tumor_detected_count,
        no_tumor_count=no_tumor_count,
        tumor_type_breakdown=tumor_type_breakdown,
        recent_scans=recent_scans
    )

@router.get("/patient/{patient_id}", response_model=List[ScanResponse])
def get_scans_by_patient(
    patient_id: str,
    session: Session = Depends(get_session),
    doctor: Doctor = Depends(get_current_doctor)
):
    statement = select(Scan).where(Scan.patient_id == patient_id, Scan.doctor_id == doctor.id).order_by(Scan.created_at.desc())
    scans = session.exec(statement).all()
    
    result = []
    for s in scans:
        result.append(ScanResponse(
            id=s.id,
            patient_id=s.patient_id,
            doctor_id=s.doctor_id,
            image_path=s.image_path,
            tumor_detected=s.tumor_detected,
            tumor_type=s.tumor_type,
            confidence_score=s.confidence_score,
            tumor_location=s.tumor_location,
            analysis_notes=s.analysis_notes,
            created_at=s.created_at.isoformat(),
            patient_name=s.patient.name if s.patient else None
        ))
    return result

@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(
    scan_id: str,
    session: Session = Depends(get_session),
    doctor: Doctor = Depends(get_current_doctor)
):
    statement = select(Scan).where(Scan.id == scan_id, Scan.doctor_id == doctor.id)
    scan = session.exec(statement).first()
    
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    
    return ScanResponse(
        id=scan.id,
        patient_id=scan.patient_id,
        doctor_id=scan.doctor_id,
        image_path=scan.image_path,
        tumor_detected=scan.tumor_detected,
        tumor_type=scan.tumor_type,
        confidence_score=scan.confidence_score,
        tumor_location=scan.tumor_location,
        analysis_notes=scan.analysis_notes,
        created_at=scan.created_at.isoformat(),
        patient_name=scan.patient.name if scan.patient else None
    )
