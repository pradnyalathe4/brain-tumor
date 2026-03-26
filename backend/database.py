from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Index, create_engine
from sqlalchemy.pool import StaticPool

from config import settings
from security import get_password_hash

def get_db_url() -> str:
    return settings.DATABASE_URL.replace("sqlite:///", "")

class Doctor(SQLModel, table=True):
    __tablename__ = "doctors"
    
    id: Optional[str] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    patients: list["Patient"] = Relationship(back_populates="doctor")
    scans: list["MRIScan"] = Relationship(back_populates="doctor")

class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    
    id: Optional[str] = Field(default=None, primary_key=True)
    doctor_id: str = Field(foreign_key="doctors.id")
    name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    medical_history: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    doctor: Doctor = Relationship(back_populates="patients")
    scans: list["MRIScan"] = Relationship(back_populates="patient")

class MRIScan(SQLModel, table=True):
    __tablename__ = "mri_scans"
    
    id: Optional[str] = Field(default=None, primary_key=True)
    patient_id: str = Field(foreign_key="patients.id", index=True)
    doctor_id: str = Field(foreign_key="doctors.id", index=True)
    scan_date: datetime = Field(default_factory=datetime.utcnow)
    image_path: str
    analysis_status: str = Field(default="completed")
    tumor_detected: Optional[bool] = None
    confidence_score: Optional[float] = None
    tumor_type: Optional[str] = None
    tumor_location: Optional[str] = None
    analysis_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    patient: Patient = Relationship(back_populates="scans")
    doctor: Doctor = Relationship(back_populates="scans")

engine = create_engine(
    f"sqlite:///{get_db_url()}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def init_default_data():
    from sqlmodel import Session
    from security import get_password_hash
    
    with Session(engine) as session:
        from sqlmodel import select
        result = session.execute(select(Doctor).where(Doctor.email == "doctor@demo.com"))
        existing = result.first()
        if not existing:
            demo_doctor = Doctor(
                id="demo-doctor-id",
                email="doctor@demo.com",
                name="Demo Doctor",
                password_hash=get_password_hash("demo123")
            )
            session.add(demo_doctor)
            session.commit()

def get_session():
    from sqlmodel import Session
    return Session(engine)