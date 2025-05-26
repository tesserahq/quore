import pytest
from uuid import UUID
from app.models.credential import Credential
from app.schemas.credential import CredentialCreate


@pytest.fixture
def test_credential_data():
    """Sample credential data for testing."""
    return {
        "name": "Test GitHub PAT",
        "type": "github_pat",
        "fields": {
            "server": "https://api.github.com",
            "user": "testuser",
            "token": "ghp_test-token-123",
        },
    }


@pytest.fixture
def test_credential_create(test_credential_data, setup_workspace):
    """Create a CredentialCreate object for testing."""
    return CredentialCreate(
        name=test_credential_data["name"],
        type=test_credential_data["type"],
        fields=test_credential_data["fields"],
        workspace_id=setup_workspace.id,
    )


@pytest.fixture
def setup_credential(db, setup_user, test_credential_create):
    """Create a test credential in the database."""
    from app.services.credential import CredentialService

    service = CredentialService(db)
    credential = service.create_credential(
        credential=test_credential_create, user_id=setup_user.id
    )
    return credential
