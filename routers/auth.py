from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from database import get_session
from models.db_models import Doctor
from security import hash_password, verify_password, create_access_token, get_current_doctor

router = APIRouter()

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    doctor: dict

class DoctorResponse(BaseModel):
    id: str
    name: str
    email: str

@router.post("/register", response_model=LoginResponse)
def register(request: RegisterRequest, session: Session = Depends(get_session)):
    statement = select(Doctor).where(Doctor.email == request.email)
    existing = session.exec(statement).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    doctor = Doctor(
        name=request.name,
        email=request.email,
        hashed_password=hash_password(request.password)
    )
    session.add(doctor)
    session.commit()
    session.refresh(doctor)
    
    token = create_access_token({"sub": doctor.id})
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        doctor={
            "id": doctor.id,
            "name": doctor.name,
            "email": doctor.email
        }
    )

@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    statement = select(Doctor).where(Doctor.email == form_data.username)
    doctor = session.exec(statement).first()
    
    if not doctor or not verify_password(form_data.password, doctor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token({"sub": doctor.id})
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        doctor={
            "id": doctor.id,
            "name": doctor.name,
            "email": doctor.email
        }
    )

@router.get("/me", response_model=DoctorResponse)
def get_me(doctor: Doctor = Depends(get_current_doctor)):
    return DoctorResponse(
        id=doctor.id,
        name=doctor.name,
        email=doctor.email
    )
