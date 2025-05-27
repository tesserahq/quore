import pytest
from app.core.system_setup import SystemSetup
from app.schemas.system import ValidationStatus, ValidationStep


def test_system_setup_success(client, db, setup_workspace):
    """Test successful system setup."""
    response = client.post("/system/setup")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "System setup completed successfully"
    assert len(data["details"]) == 1
    assert data["details"][0]["name"] == "Plugin Environment"
    assert data["details"][0]["status"] == ValidationStatus.OK
    assert "validated successfully" in data["details"][0]["message"]


@pytest.mark.parametrize(
    "mock_validation_error",
    [
        "Plugin directory not found",
        "Plugin directory not writable",
        "Invalid plugin configuration",
    ],
)
def test_system_setup_validation_error(
    client, db, setup_workspace, monkeypatch, mock_validation_error
):
    """Test system setup with validation errors."""

    # Mock the SystemSetup.validate method to return an error step
    def mock_validate():
        return [
            ValidationStep(
                name="Plugin Environment",
                status=ValidationStatus.ERROR,
                message=mock_validation_error,
            )
        ]

    monkeypatch.setattr(SystemSetup, "validate", mock_validate)

    response = client.post("/system/setup")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "System setup failed"
    assert len(data["details"]) == 1
    assert data["details"][0]["name"] == "Plugin Environment"
    assert data["details"][0]["status"] == ValidationStatus.ERROR
    assert data["details"][0]["message"] == mock_validation_error
