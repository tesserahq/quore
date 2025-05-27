import os
import json
import tempfile
from typing import Dict, Type, Any, Tuple, List
from cryptography.fernet import Fernet
from pydantic import BaseModel
from urllib.parse import urlparse

from app.constants.credentials import CredentialType
from app.schemas.credential import (
    CredentialTypeInfo,
    CredentialField,
    GithubPATModel,
    GitlabPATModel,
    SSHKeyModel,
)
from app.config import get_settings


def get_fernet():
    """Get a Fernet instance with the current master key."""
    settings = get_settings()
    return Fernet(settings.credential_master_key.encode())


def encrypt_value(value: bytes) -> bytes:
    """Encrypt a value using the master key."""
    return get_fernet().encrypt(value)


def decrypt_value(token: bytes) -> bytes:
    """Decrypt a value using the master key."""
    return get_fernet().decrypt(token)


# Define credential type schemas
github_pat_fields = [
    CredentialField(
        name="server",
        label="GitHub Server",
        type="string",
        input_type="text",
        help="GitHub API server URL (default: https://api.github.com)",
        required=True,
    ),
    CredentialField(
        name="user",
        label="User",
        type="string",
        input_type="text",
        help="GitHub username (optional)",
        required=False,
    ),
    CredentialField(
        name="token",
        label="Access Token",
        type="string",
        input_type="password",
        help="GitHub Personal Access Token with repo access",
        required=True,
    ),
]

gitlab_pat_fields = [
    CredentialField(
        name="token",
        label="GitLab Personal Access Token",
        type="string",
        input_type="password",
        help="GitLab PAT with API scope",
        required=True,
    )
]

ssh_key_fields = [
    CredentialField(
        name="private_key",
        label="SSH Private Key",
        type="string",
        input_type="textarea",
        help="Private SSH key (e.g., RSA) for Git access",
        required=True,
    ),
    CredentialField(
        name="passphrase",
        label="Key Passphrase",
        type="string",
        input_type="password",
        help="Passphrase for the SSH key (leave blank if none)",
        required=False,
    ),
]


# Credential type registry
credential_registry: Dict[CredentialType, CredentialTypeInfo] = {
    CredentialType.GITHUB_PAT: CredentialTypeInfo(
        type_name=CredentialType.GITHUB_PAT,
        display_name="GitHub Personal Access Token",
        fields=github_pat_fields,
    ),
    CredentialType.GITLAB_PAT: CredentialTypeInfo(
        type_name=CredentialType.GITLAB_PAT,
        display_name="GitLab Personal Access Token",
        fields=gitlab_pat_fields,
    ),
    CredentialType.SSH_KEY: CredentialTypeInfo(
        type_name=CredentialType.SSH_KEY,
        display_name="SSH Key",
        fields=ssh_key_fields,
    ),
}


# Model registry for validation
credential_models: Dict[CredentialType, Type[BaseModel]] = {
    CredentialType.GITHUB_PAT: GithubPATModel,
    CredentialType.GITLAB_PAT: GitlabPATModel,
    CredentialType.SSH_KEY: SSHKeyModel,
}


def get_credential_type(type_name: CredentialType) -> CredentialTypeInfo:
    """Get a credential type by name."""
    if type_name not in credential_registry:
        raise ValueError(f"Unknown credential type: {type_name}")
    return credential_registry[type_name]


def validate_credential_fields(
    type_name: CredentialType, fields: Dict[str, Any]
) -> None:
    """Validate credential fields against their model."""
    if type_name not in credential_models:
        raise ValueError(f"Unknown credential type: {type_name}")

    model = credential_models[type_name]
    try:
        model(**fields)
    except Exception as e:
        raise ValueError(f"Invalid credential fields: {str(e)}")


def encrypt_credential_fields(fields: Dict[str, Any]) -> bytes:
    """Encrypt credential fields."""
    plaintext = json.dumps(fields).encode()
    return encrypt_value(plaintext)


def decrypt_credential_fields(encrypted_data: bytes) -> Dict[str, Any]:
    """Decrypt credential fields."""
    plaintext = decrypt_value(encrypted_data)
    return json.loads(plaintext)


def apply_git_credentials(
    repo_url: str, credential_fields: Dict[str, Any]
) -> Tuple[List[str], Dict[str, str]]:
    """
    Apply Git credentials to a repository URL and return the appropriate git command and environment.

    Args:
        repo_url: The repository URL to clone
        credential_fields: The decrypted credential fields

    Returns:
        Tuple containing:
        - List of git command arguments
        - Dictionary of environment variables
    """
    parsed_url = urlparse(repo_url)
    is_ssh = parsed_url.scheme == "ssh" or parsed_url.scheme == "git"

    if is_ssh:
        if not credential_fields or "private_key" not in credential_fields:
            raise ValueError("SSH repository requires a private key credential")

        # Create temporary key file
        key_file = tempfile.NamedTemporaryFile(delete=False)
        key_file.write(credential_fields["private_key"].encode())
        key_file.close()

        # Set up SSH command with the key
        ssh_cmd = f"ssh -i {key_file.name} -o StrictHostKeyChecking=no"
        env = os.environ.copy()
        env["GIT_SSH_COMMAND"] = ssh_cmd

        return ["git", "clone", repo_url], env

    else:  # HTTPS
        if credential_fields and "token" in credential_fields:
            # Insert token into URL for authentication
            auth_url = repo_url.replace(
                "https://", f"https://{credential_fields['token']}@"
            )
            return ["git", "clone", auth_url], os.environ.copy()
        else:
            # Public repository, no authentication needed
            return ["git", "clone", repo_url], os.environ.copy()
