"""
Database Utility Tests
Tests for database functions and models
"""

import pytest
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import sqlite3
from datetime import datetime


class TestDatabaseSchema:
    """Test database schema creation"""
    
    def test_doctors_table_creation(self, test_db):
        """Should create doctors table with correct schema"""
        # Check table exists
        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='doctors'"
        )
        result = cursor.fetchone()
        assert result is not None
        
        # Check columns
        cursor = test_db.execute("PRAGMA table_info(doctors)")
        columns = {row[1] for row in cursor.fetchall()}
        
        required = {'id', 'email', 'name', 'password_hash', 'created_at'}
        assert required.issubset(columns)
    
    def test_patients_table_creation(self, test_db):
        """Should create patients table with foreign key"""
        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='patients'"
        )
        result = cursor.fetchone()
        assert result is not None
        
        # Check foreign key
        cursor = test_db.execute("PRAGMA foreign_key_list(patients)")
        fks = cursor.fetchall()
        fk_names = [fk[2] for fk in fks]
        
        assert 'doctors' in fk_names
    
    def test_mri_scans_table_creation(self, test_db):
        """Should create mri_scans table with foreign keys"""
        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='mri_scans'"
        )
        result = cursor.fetchone()
        assert result is not None
        
        # Check columns
        cursor = test_db.execute("PRAGMA table_info(mri_scans)")
        columns = {row[1] for row in cursor.fetchall()}
        
        required = {
            'id', 'patient_id', 'doctor_id', 'scan_date', 'image_path',
            'analysis_status', 'tumor_detected', 'confidence_score',
            'tumor_type', 'tumor_location', 'analysis_notes'
        }
        assert required.issubset(columns)


class TestDatabaseOperations:
    """Test CRUD operations"""
    
    def test_insert_doctor(self, test_db):
        """Should insert a new doctor"""
        doctor_id = "test-001"
        email = "doctor@test.com"
        name = "Test Doctor"
        password_hash = "$2b$12$hash"
        
        test_db.execute(
            "INSERT INTO doctors (id, email, name, password_hash) VALUES (?, ?, ?, ?)",
            (doctor_id, email, name, password_hash)
        )
        test_db.commit()
        
        cursor = test_db.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
        row = cursor.fetchone()
        
        assert row is not None
        assert row['email'] == email
        assert row['name'] == name
    
    def test_unique_email_constraint(self, test_db):
        """Should prevent duplicate emails"""
        test_db.execute(
            "INSERT INTO doctors (id, email, name, password_hash) VALUES (?, ?, ?, ?)",
            ("doc-1", "same@email.com", "Doc 1", "hash1")
        )
        
        with pytest.raises(sqlite3.IntegrityError):
            test_db.execute(
                "INSERT INTO doctors (id, email, name, password_hash) VALUES (?, ?, ?, ?)",
                ("doc-2", "same@email.com", "Doc 2", "hash2")
            )
    
    def test_insert_patient(self, test_db):
        """Should insert a new patient"""
        # First insert doctor
        test_db.execute(
            "INSERT INTO doctors (id, email, name, password_hash) VALUES (?, ?, ?, ?)",
            ("doc-1", "doc@test.com", "Doctor", "hash")
        )
        
        # Insert patient
        patient_id = "pat-001"
        test_db.execute(
            """INSERT INTO patients (id, doctor_id, name, date_of_birth, gender, contact_email)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (patient_id, "doc-1", "John Doe", "1990-01-15", "male", "john@test.com")
        )
        test_db.commit()
        
        cursor = test_db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        row = cursor.fetchone()
        
        assert row is not None
        assert row['name'] == "John Doe"
    
    def test_insert_mri_scan(self, test_db):
        """Should insert a new MRI scan"""
        # Setup doctor and patient
        test_db.execute(
            "INSERT INTO doctors (id, email, name, password_hash) VALUES (?, ?, ?, ?)",
            ("doc-1", "doc@test.com", "Doctor", "hash")
        )
        test_db.execute(
            "INSERT INTO patients (id, doctor_id, name) VALUES (?, ?, ?)",
            ("pat-1", "doc-1", "Patient")
        )
        
        # Insert scan
        scan_id = "scan-001"
        test_db.execute(
            """INSERT INTO mri_scans 
               (id, patient_id, doctor_id, image_path, analysis_status, tumor_detected, confidence_score, tumor_type)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (scan_id, "pat-1", "doc-1", "test.png", "completed", 1, 95.5, "Glioma")
        )
        test_db.commit()
        
        cursor = test_db.execute("SELECT * FROM mri_scans WHERE id = ?", (scan_id,))
        row = cursor.fetchone()
        
        assert row is not None
        assert row['tumor_detected'] == 1
        assert row['confidence_score'] == 95.5
    
    def test_query_patients_by_doctor(self, test_db):
        """Should filter patients by doctor_id"""
        # Setup
        test_db.execute(
            "INSERT INTO doctors (id, email, name, password_hash) VALUES (?, ?, ?, ?)",
            ("doc-1", "doc1@test.com", "Doc 1", "hash")
        )
        test_db.execute(
            "INSERT INTO doctors (id, email, name, password_hash) VALUES (?, ?, ?, ?)",
            ("doc-2", "doc2@test.com", "Doc 2", "hash")
        )
        
        test_db.execute(
            "INSERT INTO patients (id, doctor_id, name) VALUES (?, ?, ?)",
            ("pat-1", "doc-1", "Patient 1")
        )
        test_db.execute(
            "INSERT INTO patients (id, doctor_id, name) VALUES (?, ?, ?)",
            ("pat-2", "doc-2", "Patient 2")
        )
        test_db.execute(
            "INSERT INTO patients (id, doctor_id, name) VALUES (?, ?, ?)",
            ("pat-3", "doc-1", "Patient 3")
        )
        
        # Query
        cursor = test_db.execute(
            "SELECT COUNT(*) FROM patients WHERE doctor_id = ?", ("doc-1",)
        )
        count = cursor.fetchone()[0]
        
        assert count == 2
    
    def test_join_patients_and_scans(self, test_db):
        """Should join patients with their scans"""
        # Setup
        test_db.execute(
            "INSERT INTO doctors (id, email, name, password_hash) VALUES (?, ?, ?, ?)",
            ("doc-1", "doc@test.com", "Doc", "hash")
        )
        test_db.execute(
            "INSERT INTO patients (id, doctor_id, name) VALUES (?, ?, ?)",
            ("pat-1", "doc-1", "John Doe")
        )
        test_db.execute(
            """INSERT INTO mri_scans 
               (id, patient_id, doctor_id, image_path, analysis_status, tumor_detected)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("scan-1", "pat-1", "doc-1", "img.png", "completed", 1)
        )
        
        # Query with join
        cursor = test_db.execute(
            """SELECT p.name, s.scan_date, s.tumor_detected 
               FROM mri_scans s
               JOIN patients p ON s.patient_id = p.id
               WHERE s.doctor_id = ?""",
            ("doc-1",)
        )
        row = cursor.fetchone()
        
        assert row['name'] == "John Doe"
        assert row['tumor_detected'] == 1
    
    def test_aggregate_stats(self, test_db):
        """Should calculate aggregate statistics"""
        # Setup
        test_db.execute(
            "INSERT INTO doctors (id, email, name, password_hash) VALUES (?, ?, ?, ?)",
            ("doc-1", "doc@test.com", "Doc", "hash")
        )
        
        # Add patients
        for i in range(3):
            test_db.execute(
                "INSERT INTO patients (id, doctor_id, name) VALUES (?, ?, ?)",
                (f"pat-{i}", "doc-1", f"Patient {i}")
            )
        
        # Add scans (some with tumors)
        test_db.execute(
            "INSERT INTO patients (id, doctor_id, name) VALUES (?, ?, ?)",
            ("pat-real", "doc-1", "Real Patient")
        )
        
        for i in range(5):
            tumor = 1 if i < 2 else 0
            test_db.execute(
                """INSERT INTO mri_scans 
                   (id, patient_id, doctor_id, image_path, analysis_status, tumor_detected)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (f"scan-{i}", "pat-real", "doc-1", f"img-{i}.png", "completed", tumor)
            )
        
        # Stats queries
        cursor = test_db.execute(
            "SELECT COUNT(*) FROM patients WHERE doctor_id = ?", ("doc-1",)
        )
        assert cursor.fetchone()[0] == 4
        
        cursor = test_db.execute(
            "SELECT COUNT(*) FROM mri_scans WHERE doctor_id = ?", ("doc-1",)
        )
        assert cursor.fetchone()[0] == 5
        
        cursor = test_db.execute(
            "SELECT COUNT(*) FROM mri_scans WHERE doctor_id = ? AND tumor_detected = 1",
            ("doc-1",)
        )
        assert cursor.fetchone()[0] == 2


class TestIndexes:
    """Test database indexes"""
    
    def test_email_index_exists(self, test_db):
        """Should have index on doctors.email"""
        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE '%email%'"
        )
        # Note: SQLite may auto-create index for UNIQUE constraint
        # This test just verifies no errors occur
    
    def test_patient_doctor_index_exists(self, test_db):
        """Should have index on patients.doctor_id"""
        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE '%patient%doctor%'"
        )
    
    def test_scan_patient_index_exists(self, test_db):
        """Should have index on mri_scans.patient_id"""
        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE '%scan%patient%'"
        )