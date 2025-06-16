import pytest
from app.schemas.credential import CredentialCreate
from app.constants.credentials import CredentialType


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
def bearer_auth_credential_data():
    """Sample Bearer auth credential data for testing."""
    return {
        "name": "Test Bearer Auth",
        "type": "bearer_auth",
        "fields": {
            "token": "test-token",
        },
    }


@pytest.fixture
def basic_auth_credential_data():
    """Sample Basic auth credential data for testing."""
    return {
        "name": "Test Basic Auth",
        "type": "basic_auth",
        "fields": {
            "username": "test-user",
            "password": "test-pass",
        },
    }


@pytest.fixture
def gitlab_pat_credential_data():
    """Sample GitLab PAT credential data for testing."""
    return {
        "name": "Test GitLab PAT",
        "type": "gitlab_pat",
        "fields": {
            "token": "test-token",
        },
    }


@pytest.fixture
def ssh_key_credential_data():
    """Sample SSH key credential data for testing."""
    return {
        "name": "Test SSH Key",
        "type": "ssh_key",
        "fields": {
            "private_key": "test-key",
            "passphrase": "test-pass",
        },
    }


@pytest.fixture
def invalid_bearer_auth_credential_data():
    """Sample invalid Bearer auth credential data for testing."""
    return {
        "name": "Test Invalid Bearer Auth",
        "type": "bearer_auth",
        "fields": {},
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
def bearer_auth_credential_create(bearer_auth_credential_data, setup_workspace):
    """Create a Bearer auth CredentialCreate object for testing."""
    return CredentialCreate(
        name=bearer_auth_credential_data["name"],
        type=bearer_auth_credential_data["type"],
        fields=bearer_auth_credential_data["fields"],
        workspace_id=setup_workspace.id,
    )


@pytest.fixture
def basic_auth_credential_create(basic_auth_credential_data, setup_workspace):
    """Create a Basic auth CredentialCreate object for testing."""
    return CredentialCreate(
        name=basic_auth_credential_data["name"],
        type=basic_auth_credential_data["type"],
        fields=basic_auth_credential_data["fields"],
        workspace_id=setup_workspace.id,
    )


@pytest.fixture
def gitlab_pat_credential_create(gitlab_pat_credential_data, setup_workspace):
    """Create a GitLab PAT CredentialCreate object for testing."""
    return CredentialCreate(
        name=gitlab_pat_credential_data["name"],
        type=gitlab_pat_credential_data["type"],
        fields=gitlab_pat_credential_data["fields"],
        workspace_id=setup_workspace.id,
    )


@pytest.fixture
def ssh_key_credential_create(ssh_key_credential_data, setup_workspace):
    """Create an SSH key CredentialCreate object for testing."""
    return CredentialCreate(
        name=ssh_key_credential_data["name"],
        type=ssh_key_credential_data["type"],
        fields=ssh_key_credential_data["fields"],
        workspace_id=setup_workspace.id,
    )


@pytest.fixture
def invalid_bearer_auth_credential_create(
    invalid_bearer_auth_credential_data, setup_workspace
):
    """Create an invalid Bearer auth CredentialCreate object for testing."""
    return CredentialCreate(
        name=invalid_bearer_auth_credential_data["name"],
        type=invalid_bearer_auth_credential_data["type"],
        fields=invalid_bearer_auth_credential_data["fields"],
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


@pytest.fixture
def setup_bearer_auth_credential(db, setup_user, bearer_auth_credential_create):
    """Create a test Bearer auth credential in the database."""
    from app.services.credential import CredentialService

    service = CredentialService(db)
    credential = service.create_credential(
        credential=bearer_auth_credential_create, user_id=setup_user.id
    )
    return credential


@pytest.fixture
def setup_basic_auth_credential(db, setup_user, basic_auth_credential_create):
    """Create a test Basic auth credential in the database."""
    from app.services.credential import CredentialService

    service = CredentialService(db)
    credential = service.create_credential(
        credential=basic_auth_credential_create, user_id=setup_user.id
    )
    return credential


@pytest.fixture
def setup_gitlab_pat_credential(db, setup_user, gitlab_pat_credential_create):
    """Create a test GitLab PAT credential in the database."""
    from app.services.credential import CredentialService

    service = CredentialService(db)
    credential = service.create_credential(
        credential=gitlab_pat_credential_create, user_id=setup_user.id
    )
    return credential


@pytest.fixture
def setup_ssh_key_credential(db, setup_user, ssh_key_credential_create):
    """Create a test SSH key credential in the database."""
    from app.services.credential import CredentialService

    service = CredentialService(db)
    credential = service.create_credential(
        credential=ssh_key_credential_create, user_id=setup_user.id
    )
    return credential


@pytest.fixture
def setup_invalid_bearer_auth_credential(
    db, setup_user, invalid_bearer_auth_credential_create
):
    """Create a test invalid Bearer auth credential in the database."""
    from app.services.credential import CredentialService

    service = CredentialService(db)
    credential = service.create_credential(
        credential=invalid_bearer_auth_credential_create, user_id=setup_user.id
    )
    return credential
