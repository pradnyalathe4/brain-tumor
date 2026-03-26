"""
Backend Test Configuration
pytest configuration with fixtures for testing
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))


@pytest.fixture
def test_db():
    """Create in-memory SQLite database for testing"""
    import sqlite3
    
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            doctor_id TEXT NOT NULL,
            name TEXT NOT NULL,
            date_of_birth TEXT,
            gender TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            medical_history TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mri_scans (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            doctor_id TEXT NOT NULL,
            scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            image_path TEXT NOT NULL,
            analysis_status TEXT DEFAULT 'completed',
            tumor_detected INTEGER,
            confidence_score REAL,
            tumor_type TEXT,
            tumor_location TEXT,
            analysis_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    """)
    
    yield conn
    conn.close()


@pytest.fixture
def sample_doctor():
    """Sample doctor data for testing"""
    return {
        "id": "test-doctor-1",
        "email": "test@doctor.com",
        "name": "Test Doctor",
        "password": "testpassword123"
    }


@pytest.fixture
def sample_patient():
    """Sample patient data for testing"""
    return {
        "id": "test-patient-1",
        "doctor_id": "test-doctor-1",
        "name": "John Doe",
        "date_of_birth": "1985-03-15",
        "gender": "male",
        "contact_email": "john@example.com",
        "contact_phone": "+1234567890"
    }


@pytest.fixture
def sample_image_bytes():
    """Sample PNG image bytes for testing"""
    return bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
        0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
        0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x18, 0xDD,
        0x8D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45,
        0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
    ])


@pytest.fixture
def mock_model(monkeypatch):
    """Mock TensorFlow model for testing"""
    class MockModel:
        def predict(self, x, verbose=0):
            # Return mock predictions for 4 classes
            import numpy as np
            return np.array([[0.05, 0.05, 0.85, 0.05]])
    
    def mock_load_model(path, compile=False):
        return MockModel()
    
    monkeypatch.setattr("tensorflow.keras.models.load_model", mock_load_model)
    return MockModel()


@pytest.fixture
def app_client():
    """Create FastAPI test client"""
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create valid auth headers for testing"""
    from security import create_access_token
    token = create_access_token({"sub": "test-doctor-1"})
    return {"Authorization": f"Bearer {token}"}