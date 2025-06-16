from pydantic import BaseModel, Field, SecretStr
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from app.constants.credentials import CredentialType
from app.schemas.user import User


class CredentialField(BaseModel):
    """Schema for a credential field definition."""

    name: str
    label: str
    type: str
    input_type: str  # e.g. "password", "textarea"
    help: Optional[str] = None
    required: bool = True


class CredentialTypeInfo(BaseModel):
    """Schema for a credential type definition."""

    type_name: CredentialType
    display_name: str
    fields: List[CredentialField]


class CredentialBase(BaseModel):
    """Base schema for credential data."""

    name: str = Field(..., min_length=1, max_length=100)
    type: CredentialType
    workspace_id: UUID


class CredentialCreateRequest(BaseModel):
    """Schema for the request body when creating a credential."""

    name: str = Field(..., min_length=1, max_length=100)
    type: CredentialType
    fields: Dict[str, Any]  # The actual credential values to be encrypted


class CredentialCreate(CredentialBase):
    """Schema for creating a new credential."""

    fields: Dict[str, Any]  # The actual credential values to be encrypted


class CredentialUpdate(BaseModel):
    """Schema for updating an existing credential."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    fields: Optional[Dict[str, Any]] = None  # New credential values to be encrypted


class CredentialInfo(CredentialBase):
    """Schema for credential information (non-sensitive)."""

    id: UUID
    created_by: User
    created_at: datetime
    updated_at: datetime
    fields: Dict[str, Any] = {}  # Field values with sensitive ones obfuscated

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to extract field values with sensitive ones obfuscated."""
        # Get the base model data
        data = super().from_orm(obj)

        # Get the field definitions from the credential type
        from app.core.credentials import credential_registry

        type_info = credential_registry.get(obj.type)
        if type_info:
            # Get the decrypted fields
            from app.services.credential import CredentialService
            from app.db import get_db

            db = next(get_db())
            credential_service = CredentialService(db)
            decrypted_fields = credential_service.get_credential_fields(obj.id)

            if decrypted_fields:
                # Include all fields, but obfuscate sensitive ones
                data.fields = {
                    field.name: (
                        "[OBFUSCATED]"
                        if field.input_type in ["password", "textarea"]
                        else decrypted_fields.get(field.name)
                    )
                    for field in type_info.fields
                }

        return data


# Example credential type models
class GithubPATModel(BaseModel):
    """Model for GitHub Personal Access Token credentials."""

    server: str = Field(
        default="https://api.github.com",
        title="GitHub Server",
        description="GitHub API server URL (default: https://api.github.com)",
    )
    user: Optional[str] = Field(
        default=None,
        title="User",
        description="GitHub username (optional)",
    )
    token: SecretStr = Field(
        ...,
        title="Access Token",
        description="GitHub Personal Access Token with repo access",
    )


class GitlabPATModel(BaseModel):
    """Model for GitLab Personal Access Token credentials."""

    token: SecretStr = Field(
        ...,
        title="GitLab Personal Access Token",
        description="GitLab PAT with API scope",
    )


class SSHKeyModel(BaseModel):
    """Model for SSH Key credentials."""

    private_key: SecretStr = Field(
        ..., title="SSH Private Key", description="Private SSH key content"
    )
    passphrase: Optional[SecretStr] = Field(
        None, title="Key Passphrase", description="Passphrase for the SSH key"
    )


class BearerAuthModel(BaseModel):
    """Model for Bearer Authentication credentials."""

    token: SecretStr = Field(
        ...,
        title="Bearer Token",
        description="Bearer token for API authentication",
    )


class BasicAuthModel(BaseModel):
    """Model for Basic Authentication credentials."""

    username: str = Field(
        ...,
        title="Username",
        description="Username for basic authentication",
    )
    password: SecretStr = Field(
        ...,
        title="Password",
        description="Password for basic authentication",
    )
