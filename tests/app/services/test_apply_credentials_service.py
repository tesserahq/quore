import pytest
from uuid import uuid4
from app.constants.credentials import CredentialType
from app.services.credential_service import CredentialService
from app.core.credentials import (
    get_credential_type,
    validate_credential_fields,
    encrypt_credential_fields,
    decrypt_credential_fields,
)


@pytest.fixture
def credential_service(db):
    return CredentialService(db)


def test_get_credential_type():
    """Test getting credential type info."""
    # Test valid types
    github_type = get_credential_type(CredentialType.GITHUB_PAT)
    assert github_type.type_name == CredentialType.GITHUB_PAT
    assert github_type.display_name == "GitHub Personal Access Token"
    assert len(github_type.fields) == 3

    gitlab_type = get_credential_type(CredentialType.GITLAB_PAT)
    assert gitlab_type.type_name == CredentialType.GITLAB_PAT
    assert gitlab_type.display_name == "GitLab Personal Access Token"
    assert len(gitlab_type.fields) == 1

    ssh_type = get_credential_type(CredentialType.SSH_KEY)
    assert ssh_type.type_name == CredentialType.SSH_KEY
    assert ssh_type.display_name == "SSH Key"
    assert len(ssh_type.fields) == 2

    bearer_type = get_credential_type(CredentialType.BEARER_AUTH)
    assert bearer_type.type_name == CredentialType.BEARER_AUTH
    assert bearer_type.display_name == "Bearer Authentication"
    assert len(bearer_type.fields) == 1

    basic_type = get_credential_type(CredentialType.BASIC_AUTH)
    assert basic_type.type_name == CredentialType.BASIC_AUTH
    assert basic_type.display_name == "Basic Authentication"
    assert len(basic_type.fields) == 2

    # Test invalid type
    with pytest.raises(ValueError):
        get_credential_type("invalid_type")


def test_validate_credential_fields():
    """Test validating credential fields."""
    # Test valid fields
    validate_credential_fields(
        CredentialType.GITHUB_PAT,
        {"server": "https://api.github.com", "token": "test-token"},
    )
    validate_credential_fields(CredentialType.GITLAB_PAT, {"token": "test-token"})
    validate_credential_fields(
        CredentialType.SSH_KEY,
        {"private_key": "test-key", "passphrase": "test-pass"},
    )
    validate_credential_fields(CredentialType.BEARER_AUTH, {"token": "test-token"})
    validate_credential_fields(
        CredentialType.BASIC_AUTH,
        {"username": "test-user", "password": "test-pass"},
    )

    # Test invalid fields
    with pytest.raises(ValueError):
        validate_credential_fields(CredentialType.GITHUB_PAT, {})
    with pytest.raises(ValueError):
        validate_credential_fields(CredentialType.GITLAB_PAT, {})
    with pytest.raises(ValueError):
        validate_credential_fields(CredentialType.SSH_KEY, {})
    with pytest.raises(ValueError):
        validate_credential_fields(CredentialType.BEARER_AUTH, {})
    with pytest.raises(ValueError):
        validate_credential_fields(CredentialType.BASIC_AUTH, {})


def test_encrypt_decrypt_credential_fields():
    """Test encrypting and decrypting credential fields."""
    test_fields = {
        "server": "https://api.github.com",
        "token": "test-token",
        "user": "test-user",
    }

    # Encrypt fields
    encrypted = encrypt_credential_fields(test_fields)
    assert isinstance(encrypted, bytes)
    assert encrypted != test_fields

    # Decrypt fields
    decrypted = decrypt_credential_fields(encrypted)
    assert decrypted == test_fields


def test_apply_credentials_bearer_auth(
    credential_service, setup_bearer_auth_credential
):
    """Test applying Bearer auth credentials."""
    headers = credential_service.apply_credentials(setup_bearer_auth_credential.id)
    assert headers == {"Authorization": "Bearer test-token"}


def test_apply_credentials_basic_auth(credential_service, setup_basic_auth_credential):
    """Test applying Basic auth credentials."""
    headers = credential_service.apply_credentials(setup_basic_auth_credential.id)
    assert headers == {"Authorization": "Basic dGVzdC11c2VyOnRlc3QtcGFzcw=="}


def test_apply_credentials_github_pat(credential_service, setup_credential):
    """Test applying GitHub PAT credentials."""
    headers = credential_service.apply_credentials(setup_credential.id)
    assert headers == {"Authorization": "Bearer ghp_test-token-123"}


def test_apply_credentials_gitlab_pat(credential_service, setup_gitlab_pat_credential):
    """Test applying GitLab PAT credentials."""
    headers = credential_service.apply_credentials(setup_gitlab_pat_credential.id)
    assert headers == {"Authorization": "Bearer test-token"}


def test_apply_credentials_ssh_key(credential_service, setup_ssh_key_credential):
    """Test applying SSH key credentials."""
    # SSH key type should not modify headers
    headers = credential_service.apply_credentials(setup_ssh_key_credential.id)
    assert headers == {}


def test_apply_credentials_not_found(credential_service):
    """Test applying non-existent credentials."""
    with pytest.raises(ValueError):
        credential_service.apply_credentials(uuid4())


def test_apply_credentials_missing_token(
    credential_service, setup_bearer_auth_credential, db
):
    """Test applying credentials with missing token."""
    # Set fields to a dictionary that's missing the token field
    setup_bearer_auth_credential.encrypted_data = encrypt_credential_fields(
        {"other_field": "value"}
    )
    db.commit()

    with pytest.raises(ValueError, match="Bearer auth requires a token field"):
        credential_service.apply_credentials(setup_bearer_auth_credential.id)
