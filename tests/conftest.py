import pytest
import os
import tempfile

@pytest.fixture
def test_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_url = f"sqlite:///{f.name}"
    
    os.environ["DATABASE_URL"] = db_url
    
    yield db_url
    
    os.unlink(f.name)

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)
