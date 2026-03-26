"""
End-to-End Tests for NeuroScan AI
Tests the full user journey: register → login → create patient → upload MRI → get prediction
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
TEST_PASSWORD = "testpassword123"
TEST_PATIENT_NAME = "Test Patient"

# Create a simple test image (1x1 pixel PNG)
TEST_IMAGE_BYTES = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,  # 8-bit RGB
    0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
    0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,  
    0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x18, 0xDD,
    0x8D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45,  # IEND chunk
    0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
])


class TestNeuroScanE2E:
    """End-to-end tests for the complete user journey"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup before each test"""
        self.base_url = BASE_URL
        self.token = None
        self.doctor_id = None
        self.patient_id = None
    
    @pytest.mark.asyncio
    async def test_full_user_journey(self):
        """Test complete user journey: register → login → create patient → upload MRI → check results"""
        
        # Step 1: Register a new doctor
        print("\n1. Testing doctor registration...")
        register_data = {
            "email": TEST_EMAIL,
            "name": "Test Doctor",
            "password": TEST_PASSWORD
        }
        
        async with asyncio.timeout(10):
            response = await self._make_request(
                "/api/auth/register",
                method="POST",
                data=register_data
            )
        
        assert response is not None, "Registration should return data"
        assert "access_token" in response, "Should receive access token"
        assert "doctor" in response, "Should receive doctor info"
        
        self.token = response["access_token"]
        self.doctor_id = response["doctor"]["id"]
        print(f"✓ Doctor registered: {TEST_EMAIL}")
        
        # Step 2: Login with the new account
        print("\n2. Testing doctor login...")
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        async with asyncio.timeout(10):
            response = await self._make_request(
                "/api/auth/login",
                method="POST",
                data=login_data
            )
        
        assert response is not None, "Login should return data"
        assert "access_token" in response, "Should receive access token"
        print(f"✓ Doctor logged in successfully")
        
        # Step 3: Create a patient
        print("\n3. Testing patient creation...")
        patient_data = {
            "name": TEST_PATIENT_NAME,
            "date_of_birth": "1990-01-15",
            "gender": "male",
            "contact_email": "patient@example.com",
            "contact_phone": "+1234567890"
        }
        
        async with asyncio.timeout(10):
            response = await self._make_request(
                "/api/patients",
                method="POST",
                data=patient_data,
                auth=True
            )
        
        assert response is not None, "Patient creation should return data"
        assert "id" in response, "Should receive patient ID"
        
        self.patient_id = response["id"]
        print(f"✓ Patient created: {TEST_PATIENT_NAME}")
        
        # Step 4: Get patient list
        print("\n4. Testing patient list retrieval...")
        async with asyncio.timeout(10):
            response = await self._make_request(
                "/api/patients",
                method="GET",
                auth=True
            )
        
        assert response is not None, "Should return patient list"
        assert isinstance(response, list), "Should return list of patients"
        assert len(response) > 0, "Should have at least one patient"
        print(f"✓ Retrieved {len(response)} patient(s)")
        
        # Step 5: Upload MRI and get prediction
        print("\n5. Testing MRI upload and prediction...")
        
        # Create temp image file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(TEST_IMAGE_BYTES)
            tmp_path = tmp.name
        
        try:
            async with asyncio.timeout(30):
                response = await self._upload_and_predict(
                    tmp_path,
                    self.patient_id,
                    self.doctor_id
                )
            
            assert response is not None, "Prediction should return data"
            assert "tumor_detected" in response, "Should include tumor detection result"
            assert "confidence_score" in response, "Should include confidence score"
            assert "analysis_notes" in response, "Should include analysis notes"
            
            print(f"✓ Prediction completed:")
            print(f"  - Tumor detected: {response['tumor_detected']}")
            print(f"  - Confidence: {response['confidence_score']}%")
            print(f"  - Type: {response.get('tumor_type', 'N/A')}")
        finally:
            os.unlink(tmp_path)
        
        # Step 6: Check scan history
        print("\n6. Testing scan history retrieval...")
        async with asyncio.timeout(10):
            response = await self._make_request(
                "/api/scans",
                method="GET",
                auth=True
            )
        
        assert response is not None, "Should return scan list"
        assert isinstance(response, list), "Should return list of scans"
        assert len(response) > 0, "Should have at least one scan"
        
        scan = response[0]
        assert "patient_name" in scan, "Should include patient name"
        assert "confidence_score" in scan, "Should include confidence"
        
        print(f"✓ Retrieved {len(response)} scan(s)")
        
        # Step 7: Check stats
        print("\n7. Testing stats retrieval...")
        async with asyncio.timeout(10):
            response = await self._make_request(
                "/api/stats",
                method="GET",
                auth=True
            )
        
        assert response is not None, "Should return stats"
        assert "total_patients" in response, "Should include patient count"
        assert "total_scans" in response, "Should include scan count"
        
        print(f"✓ Stats: {response['total_patients']} patients, {response['total_scans']} scans")
        
        print("\n✅ All tests passed!")
    
    async def _make_request(self, endpoint, method="GET", data=None, auth=False):
        """Make HTTP request to the API"""
        import aiohttp
        
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, headers=headers) as response:
                    return await response.json()
            elif method == "POST":
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status >= 400:
                        error = await response.json()
                        raise Exception(error.get("detail", "Request failed"))
                    return await response.json()
    
    async def _upload_and_predict(self, file_path, patient_id, doctor_id):
        """Upload file and get prediction"""
        import aiohttp
        
        url = f"{self.base_url}/predict"
        
        form_data = aiohttp.FormData()
        form_data.add_field('file', open(file_path, 'rb'), filename='test.png', content_type='image/png')
        form_data.add_field('patient_id', patient_id)
        form_data.add_field('doctor_id', doctor_id)
        
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form_data, headers=headers) as response:
                if response.status >= 400:
                    error = await response.json()
                    raise Exception(error.get("detail", "Prediction failed"))
                return await response.json()


async def run_tests():
    """Run the E2E tests"""
    print("=" * 60)
    print("NeuroScan AI - End-to-End Tests")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print()
    
    # Check if server is running
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/") as response:
                print(f"✓ Server is running (status: {response.status})")
    except Exception as e:
        print(f"✗ Server not accessible: {e}")
        print("Please start the server first: cd backend && python main.py")
        return
    
    # Run tests
    test = TestNeuroScanE2E()
    try:
        await test.test_full_user_journey()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_tests())