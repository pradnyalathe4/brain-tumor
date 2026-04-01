from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from database import get_session
from models.db_models import Patient, Doctor
from security import get_current_doctor

router = APIRouter()

class PatientCreate(BaseModel):
    name: str
    date_of_birth: date
    gender: str
    contact_email: Optional[str] = None
    notes: Optional[str] = None

class PatientResponse(BaseModel):
    id: str
    name: str
    date_of_birth: date
    gender: str
    contact_email: Optional[str]
    notes: Optional[str]
    doctor_id: str
    created_at: str
    scans_count: int = 0

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    contact_email: Optional[str] = None
    notes: Optional[str] = None

@router.get("", response_model=List[PatientResponse])
def list_patients(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    doctor: Doctor = Depends(get_current_doctor)
):
    statement = select(Patient).where(Patient.doctor_id == doctor.id).offset(skip).limit(limit)
    patients = session.exec(statement).all()
    
    result = []
    for p in patients:
        result.append(PatientResponse(
            id=p.id,
            name=p.name,
            date_of_birth=p.date_of_birth,
            gender=p.gender,
            contact_email=p.contact_email,
            notes=p.notes,
            doctor_id=p.doctor_id,
            created_at=p.created_at.isoformat(),
            scans_count=len(p.scans) if p.scans else 0
        ))
    return result

@router.post("", response_model=PatientResponse)
def create_patient(
    patient: PatientCreate,
    session: Session = Depends(get_session),
    doctor: Doctor = Depends(get_current_doctor)
):
    db_patient = Patient(
        name=patient.name,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        contact_email=patient.contact_email,
        notes=patient.notes,
        doctor_id=doctor.id
    )
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    
    return PatientResponse(
        id=db_patient.id,
        name=db_patient.name,
        date_of_birth=db_patient.date_of_birth,
        gender=db_patient.gender,
        contact_email=db_patient.contact_email,
        notes=db_patient.notes,
        doctor_id=db_patient.doctor_id,
        created_at=db_patient.created_at.isoformat(),
        scans_count=0
    )

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: str,
    session: Session = Depends(get_session),
    doctor: Doctor = Depends(get_current_doctor)
):
    statement = select(Patient).where(Patient.id == patient_id, Patient.doctor_id == doctor.id)
    patient = session.exec(statement).first()
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    return PatientResponse(
        id=patient.id,
        name=patient.name,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        contact_email=patient.contact_email,
        notes=patient.notes,
        doctor_id=patient.doctor_id,
        created_at=patient.created_at.isoformat(),
        scans_count=len(patient.scans) if patient.scans else 0
    )

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: str,
    patient_update: PatientUpdate,
    session: Session = Depends(get_session),
    doctor: Doctor = Depends(get_current_doctor)
):
    statement = select(Patient).where(Patient.id == patient_id, Patient.doctor_id == doctor.id)
    patient = session.exec(statement).first()
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    if patient_update.name is not None:
        patient.name = patient_update.name
    if patient_update.date_of_birth is not None:
        patient.date_of_birth = patient_update.date_of_birth
    if patient_update.gender is not None:
        patient.gender = patient_update.gender
    if patient_update.contact_email is not None:
        patient.contact_email = patient_update.contact_email
    if patient_update.notes is not None:
        patient.notes = patient_update.notes
    
    session.commit()
    session.refresh(patient)
    
    return PatientResponse(
        id=patient.id,
        name=patient.name,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        contact_email=patient.contact_email,
        notes=patient.notes,
        doctor_id=patient.doctor_id,
        created_at=patient.created_at.isoformat(),
        scans_count=len(patient.scans) if patient.scans else 0
    )

@router.delete("/{patient_id}")
def delete_patient(
    patient_id: str,
    session: Session = Depends(get_session),
    doctor: Doctor = Depends(get_current_doctor)
):
    statement = select(Patient).where(Patient.id == patient_id, Patient.doctor_id == doctor.id)
    patient = session.exec(statement).first()
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    session.delete(patient)
    session.commit()
    
    return {"message": "Patient deleted successfully"}
