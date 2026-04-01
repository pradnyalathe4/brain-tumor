from datetime import datetime, date, timezone
from typing import Optional, List
import uuid
from sqlmodel import Field, SQLModel, Relationship

class Doctor(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    patients: List["Patient"] = Relationship(back_populates="doctor")
    scans: List["Scan"] = Relationship(back_populates="doctor")

class Patient(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    date_of_birth: date
    gender: str
    contact_email: Optional[str] = None
    notes: Optional[str] = None
    doctor_id: str = Field(foreign_key="doctor.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    doctor: Optional[Doctor] = Relationship(back_populates="patients")
    scans: List["Scan"] = Relationship(back_populates="patient")

class Scan(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    patient_id: Optional[str] = Field(default=None, foreign_key="patient.id", nullable=True)
    doctor_id: str = Field(foreign_key="doctor.id")
    image_path: str
    tumor_detected: bool
    tumor_type: str
    confidence_score: float
    tumor_location: Optional[str] = None
    analysis_notes: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    patient: Optional[Patient] = Relationship(back_populates="scans")
    doctor: Optional[Doctor] = Relationship(back_populates="scans")
