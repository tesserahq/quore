from uuid import uuid4
from app.services.credential import CredentialService
from app.schemas.credential import CredentialUpdate


def test_create_credential(db, setup_user, test_credential_create):
    """Test creating a new credential."""
    service = CredentialService(db)
    credential = service.create_credential(
        credential=test_credential_create, user_id=setup_user.id
    )

    assert credential is not None
    assert credential.name == test_credential_create.name
    assert credential.type == test_credential_create.type
    assert credential.workspace_id == test_credential_create.workspace_id
    assert credential.created_by_id == setup_user.id
    assert credential.encrypted_data is not None


def test_get_credential(db, setup_credential):
    """Test retrieving a credential by ID."""
    service = CredentialService(db)
    credential = setup_credential
    retrieved_credential = service.get_credential(credential.id)

    assert retrieved_credential is not None
    assert retrieved_credential.id == credential.id
    assert retrieved_credential.name == credential.name
    assert retrieved_credential.type == credential.type


def test_get_nonexistent_credential(db):
    """Test retrieving a non-existent credential."""
    service = CredentialService(db)
    credential = service.get_credential(uuid4())
    assert credential is None


def test_get_credentials(db, setup_credential):
    """Test retrieving all credentials with pagination."""
    service = CredentialService(db)
    credential = setup_credential
    credentials = service.get_credentials(skip=0, limit=10)

    assert len(credentials) > 0
    assert any(c.id == credential.id for c in credentials)


def test_get_workspace_credentials(db, setup_credential):
    """Test retrieving credentials for a specific workspace."""
    service = CredentialService(db)
    credential = setup_credential
    credentials = service.get_workspace_credentials(
        workspace_id=credential.workspace_id, skip=0, limit=10
    )

    assert len(credentials) > 0
    assert all(c.workspace_id == credential.workspace_id for c in credentials)


def test_get_user_credentials(db, setup_credential, setup_user):
    """Test retrieving credentials created by a specific user."""
    service = CredentialService(db)
    _credential = setup_credential
    credentials = service.get_user_credentials(user_id=setup_user.id, skip=0, limit=10)

    assert len(credentials) > 0
    assert all(c.created_by_id == setup_user.id for c in credentials)


def test_update_credential(db, setup_credential):
    """Test updating a credential."""
    service = CredentialService(db)
    credential = setup_credential
    original_encrypted_data = credential.encrypted_data

    update_data = CredentialUpdate(
        name="Updated GitHub PAT", fields={"token": "ghp_updated-token-789"}
    )

    updated_credential = service.update_credential(
        credential_id=credential.id, credential=update_data
    )

    assert updated_credential is not None
    assert updated_credential.name == update_data.name
    assert updated_credential.encrypted_data != original_encrypted_data


def test_update_nonexistent_credential(db):
    """Test updating a non-existent credential."""
    service = CredentialService(db)
    update_data = CredentialUpdate(name="Updated Name")

    updated_credential = service.update_credential(
        credential_id=uuid4(), credential=update_data
    )
    assert updated_credential is None


def test_delete_credential(db, setup_credential):
    """Test deleting a credential."""
    service = CredentialService(db)
    credential = setup_credential
    result = service.delete_credential(credential.id)

    assert result is True
    deleted_credential = service.get_credential(credential.id)
    assert deleted_credential is None


def test_delete_nonexistent_credential(db):
    """Test deleting a non-existent credential."""
    service = CredentialService(db)
    result = service.delete_credential(uuid4())
    assert result is False


def test_get_credential_fields(db, setup_credential, test_credential_data):
    """Test retrieving decrypted credential fields."""
    service = CredentialService(db)
    credential = setup_credential
    fields = service.get_credential_fields(credential.id)

    assert fields is not None
    assert fields == test_credential_data["fields"]


def test_search_credentials(db, setup_credential):
    """Test searching credentials with filters."""
    service = CredentialService(db)
    credential = setup_credential

    # Search by name
    results = service.search({"name": credential.name})
    assert len(results) > 0
    assert all(c.name == credential.name for c in results)

    # Search by type
    results = service.search({"type": credential.type})
    assert len(results) > 0
    assert all(c.type == credential.type for c in results)

    # Search with non-existent criteria
    results = service.search({"name": "nonexistent"})
    assert len(results) == 0
