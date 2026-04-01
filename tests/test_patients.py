import pytest

class TestPatientsAPI:
    def test_list_patients_requires_auth(self, client):
        res = client.get("/api/patients")
        assert res.status_code == 401
    
    def test_create_patient_validation(self):
        pass
    
    def test_get_patient_not_found(self):
        pass
