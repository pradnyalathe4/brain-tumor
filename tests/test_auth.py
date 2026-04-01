import pytest
from datetime import datetime, timedelta, timezone

from security import create_access_token, verify_token, hash_password, verify_password, decode_token

class TestPasswordHashing:
    def test_hash_generates_unique_salts(self):
        hash1 = hash_password("testpassword")
        hash2 = hash_password("testpassword")
        assert hash1 != hash2
    
    def test_verify_correct_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True
    
    def test_verify_wrong_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False
    
    def test_verify_empty_passwords(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True

class TestJWTGeneration:
    def test_create_token_contains_doctor_id(self):
        token = create_access_token({"sub": "doctor-123"})
        payload = verify_token(token)
        assert payload["sub"] == "doctor-123"
    
    def test_decode_invalid_token(self):
        result = decode_token("invalid-token")
        assert result is None
    
    def test_decode_empty_token(self):
        result = decode_token("")
        assert result is None
    
    def test_token_has_expiration(self):
        token = create_access_token({"sub": "doctor-123"})
        payload = verify_token(token)
        assert payload["exp"] is not None
    
    def test_token_with_custom_expiry(self):
        from datetime import timezone
        import time
        
        token = create_access_token({"sub": "doctor-123"})
        payload = verify_token(token)
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        
        # Token should have default 24 hour expiry
        expected = datetime.now(timezone.utc) + timedelta(hours=24)
        assert abs((exp - expected).total_seconds()) < 10

class TestErrorHandling:
    def test_malformed_base64_in_token(self):
        result = decode_token("not.a.valid.jwt.token")
        assert result is None
    
    def test_missing_sub_in_payload(self):
        from jose import jwt
        import time
        token = jwt.encode({"exp": time.time() + 3600}, "secret", algorithm="HS256")
        result = decode_token(token)
        assert result is None
