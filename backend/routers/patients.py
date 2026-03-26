from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from schemas import PatientCreate, PatientResponse, ScanResponse, StatsResponse
from database import get_session, Doctor, Patient, MRIScan
from routers.auth import get_current_doctor
from exceptions import ResourceNotFoundError

router = APIRouter(prefix="/api", tags=["Patients"])

@router.get("/patients", response_model=list[PatientResponse])
async def get_patients(
    current_doctor: Doctor = Depends(get_current_doctor),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Patient)
        .where(Patient.doctor_id == current_doctor.id)
        .order_by(Patient.created_at.desc())
    )
    return result.all()

@router.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    data: PatientCreate,
    current_doctor: Doctor = Depends(get_current_doctor),
    session: AsyncSession = Depends(get_session)
):
    import uuid
    patient = Patient(
        id=str(uuid.uuid4()),
        doctor_id=current_doctor.id,
        name=data.name,
        date_of_birth=data.date_of_birth,
        gender=data.gender.value if data.gender else None,
        contact_email=data.contact_email,
        contact_phone=data.contact_phone,
        medical_history=data.medical_history
    )
    session.add(patient)
    await session.commit()
    await session.refresh(patient)
    return patient

@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    current_doctor: Doctor = Depends(get_current_doctor),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.doctor_id == current_doctor.id
        )
    )
    patient = result.first()
    if not patient:
        raise ResourceNotFoundError("Patient")
    return patient

@router.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str,
    current_doctor: Doctor = Depends(get_current_doctor),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.doctor_id == current_doctor.id
        )
    )
    patient = result.first()
    if not patient:
        raise ResourceNotFoundError("Patient")
    
    await session.delete(patient)
    await session.commit()

@router.get("/scans", response_model=list[ScanResponse])
async def get_scans(
    current_doctor: Doctor = Depends(get_current_doctor),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(MRIScan, Patient.name)
        .join(Patient, MRIScan.patient_id == Patient.id)
        .where(MRIScan.doctor_id == current_doctor.id)
        .order_by(MRIScan.created_at.desc())
    )
    
    scans = []
    for scan, patient_name in result.all():
        scan_dict = scan.__dict__.copy()
        scan_dict["patient_name"] = patient_name
        scans.append(scan_dict)
    return scans

@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_doctor: Doctor = Depends(get_current_doctor),
    session: AsyncSession = Depends(get_session)
):
    patients_result = await session.execute(
        select(func.count(Patient.id)).where(Patient.doctor_id == current_doctor.id)
    )
    total_patients = patients_result.scalar() or 0
    
    scans_result = await session.execute(
        select(func.count(MRIScan.id)).where(MRIScan.doctor_id == current_doctor.id)
    )
    total_scans = scans_result.scalar() or 0
    
    tumors_result = await session.execute(
        select(func.count(MRIScan.id)).where(
            MRIScan.doctor_id == current_doctor.id,
            MRIScan.tumor_detected == True
        )
    )
    tumors_detected = tumors_result.scalar() or 0
    
    tumor_types_result = await session.execute(
        select(MRIScan.tumor_type, func.count(MRIScan.id))
        .where(
            MRIScan.doctor_id == current_doctor.id,
            MRIScan.tumor_detected == True
        )
        .group_by(MRIScan.tumor_type)
    )
    tumor_types = {row[0]: row[1] for row in tumor_types_result.all() if row[0]}
    
    return StatsResponse(
        total_patients=total_patients,
        total_scans=total_scans,
        tumors_detected=tumors_detected,
        tumor_types=tumor_types,
        monthly_scans={}
    )