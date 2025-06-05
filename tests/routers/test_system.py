import pytest
from app.core.system_setup import SystemSetup
from app.schemas.system import ValidationStatus, ValidationStep


def test_system_setup_success(client):
    """Test successful system setup."""
    response = client.post("/system/setup")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "System setup completed successfully"
    assert data["success"] is True
    assert len(data["details"]) == 2
    assert data["details"][0]["name"] == "Credential Master Key"
    assert data["details"][0]["status"] == ValidationStatus.OK
    assert "validated successfully" in data["details"][0]["message"]
