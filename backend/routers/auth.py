from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from schemas import DoctorRegister, DoctorLogin, TokenResponse, DoctorResponse
from database import get_session, Doctor
from security import verify_password, create_access_token, get_password_hash, decode_token
from exceptions import AuthError

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

async def get_current_doctor(
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session)
) -> Doctor:
    if not authorization:
        raise AuthError("Authorization header required", status_code=401)
    
    token = authorization.replace("Bearer ", "")
    token_data = decode_token(token)
    
    if not token_data:
        raise AuthError("Invalid or expired token", status_code=401)
    
    from sqlmodel import select
    result = await session.execute(
        select(Doctor).where(Doctor.id == token_data.doctor_id)
    )
    doctor = result.first()
    
    if not doctor:
        raise AuthError("Doctor not found", status_code=404)
    
    return doctor

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: DoctorRegister,
    session: AsyncSession = Depends(get_session)
):
    from sqlmodel import select
    
    existing = await session.execute(
        select(Doctor).where(Doctor.email == data.email)
    )
    if existing.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    doctor = Doctor(
        id=f"doc-{data.email.split('@')[0]}",
        email=data.email,
        name=data.name,
        password_hash=get_password_hash(data.password)
    )
    session.add(doctor)
    await session.commit()
    await session.refresh(doctor)
    
    access_token = create_access_token({"sub": doctor.id})
    
    return TokenResponse(
        access_token=access_token,
        doctor=DoctorResponse(
            id=doctor.id,
            email=doctor.email,
            name=doctor.name
        )
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    data: DoctorLogin,
    session: AsyncSession = Depends(get_session)
):
    from sqlmodel import select
    
    result = await session.execute(
        select(Doctor).where(Doctor.email == data.email)
    )
    doctor = result.first()
    
    if not doctor or not verify_password(data.password, doctor.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token({"sub": doctor.id})
    
    return TokenResponse(
        access_token=access_token,
        doctor=DoctorResponse(
            id=doctor.id,
            email=doctor.email,
            name=doctor.name
        )
    )

@router.get("/me", response_model=DoctorResponse)
async def get_current_user(
    current_doctor: Doctor = Depends(get_current_doctor)
):
    return DoctorResponse(
        id=current_doctor.id,
        email=current_doctor.email,
        name=current_doctor.name,
        created_at=current_doctor.created_at
    )