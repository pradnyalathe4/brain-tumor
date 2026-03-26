"""
Authentication Tests
Unit tests for security module: password hashing, JWT validation
"""

import pytest
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token
)


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_hash_generates_unique_salts(self):
        """Same password should generate different hashes"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert hash1.startswith("$2b$")
    
    def test_verify_correct_password(self):
        """Should return True for correct password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_wrong_password(self):
        """Should return False for wrong password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_empty_passwords(self):
        """Should handle empty passwords correctly"""
        hashed = get_password_hash("")
        
        assert verify_password("", hashed) is True
        assert verify_password(" ", hashed) is False


class TestJWTGeneration:
    """Test JWT token functions"""
    
    def test_create_token_contains_doctor_id(self):
        """Token should contain doctor_id in payload"""
        doctor_id = "test-doctor-123"
        token = create_access_token({"sub": doctor_id})
        
        # Decode and verify
        payload = decode_token(token)
        
        assert payload is not None
        assert payload.doctor_id == doctor_id
    
    def test_decode_invalid_token(self):
        """Should return None for invalid token"""
        result = decode_token("invalid.token.here")
        assert result is None
    
    def test_decode_empty_token(self):
        """Should return None for empty token"""
        result = decode_token("")
        assert result is None
    
    def test_token_has_expiration(self):
        """Token should have expiration timestamp"""
        from datetime import timezone
        
        doctor_id = "test-doctor-123"
        token = create_access_token({"sub": doctor_id})
        
        payload = decode_token(token)
        assert payload.exp is not None
        assert payload.exp > datetime.now(timezone.utc)
    
    def test_token_with_custom_expiry(self):
        """Token with custom expiry should work"""
        from datetime import timezone
        doctor_id = "test-doctor-123"
        custom_expiry = timedelta(hours=48)
        
        before = datetime.now(timezone.utc)
        token = create_access_token(
            {"sub": doctor_id},
            expires_delta=custom_expiry
        )
        after = datetime.now(timezone.utc)
        
        payload = decode_token(token)
        expected_expiry = before + custom_expiry
        
        assert payload.exp is not None
        assert abs((payload.exp - expected_expiry).total_seconds()) < 10
    
    def test_token_invalid_signature(self):
        """Token with wrong secret should be invalid"""
        import base64
        import json
        import hashlib
        
        doctor_id = "test-doctor-123"
        
        # Create token with different secret
        payload = {
            "sub": doctor_id,
            "exp": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        data = base64.b64encode(json.dumps(payload).encode()).decode()
        wrong_sig = hashlib.sha256((data + "wrong-secret").encode()).hexdigest()
        token = f"{data}.{wrong_sig}"
        
        result = decode_token(token)
        assert result is None


class TestErrorHandling:
    """Test error handling in security module"""
    
    def test_malformed_base64_in_token(self):
        """Should handle malformed base64 gracefully"""
        result = decode_token("not-valid-base64!!!.signature")
        assert result is None
    
    def test_missing_sub_in_payload(self):
        """Should return None if sub is missing"""
        import base64
        import json
        from datetime import datetime, timedelta
        
        payload = {
            "exp": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        data = base64.b64encode(json.dumps(payload).encode()).decode()
        token = f"{data}.fakesignature"
        
        result = decode_token(token)
        # Should fail because sub is missing
        assert result is None


# Import for datetime tests
from datetime import datetime, timedelta