from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging

from app.models.credential import Credential
from app.schemas.credential import CredentialCreate, CredentialUpdate, CredentialInfo
from app.utils.db.filtering import apply_filters
from app.core.credentials import (
    validate_credential_fields,
    encrypt_credential_fields,
    decrypt_credential_fields,
    credential_registry,
)
from app.constants.credentials import CredentialType
from app.core.logging_config import get_logger

logger = get_logger()


class CredentialService:
    def __init__(self, db: Session):
        self.db = db

    def get_credential(self, credential_id: UUID) -> Optional[Credential]:
        """Get a credential by its ID."""
        logger.info(f"Looking up credential {credential_id}")
        credential = (
            self.db.query(Credential).filter(Credential.id == credential_id).first()
        )
        if credential:
            logger.info(
                f"Found credential {credential_id} in workspace {credential.workspace_id}"
            )
        else:
            logger.warning(f"Credential {credential_id} not found")
        return credential

    def get_credentials(self, skip: int = 0, limit: int = 100) -> List[Credential]:
        """Get all credentials with pagination."""
        return self.db.query(Credential).offset(skip).limit(limit).all()

    def get_workspace_credentials(
        self, workspace_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Credential]:
        """Get all credentials for a specific workspace."""
        return (
            self.db.query(Credential)
            .filter(Credential.workspace_id == workspace_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_credentials(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Credential]:
        """Get all credentials created by a specific user."""
        return (
            self.db.query(Credential)
            .filter(Credential.created_by_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_credential(
        self, credential: CredentialCreate, user_id: UUID
    ) -> Credential:
        """Create a new credential."""
        # Validate the credential fields against the type's schema
        validate_credential_fields(credential.type, credential.fields)

        # Encrypt the credential fields
        encrypted_data = encrypt_credential_fields(credential.fields)

        # Create the credential record
        db_credential = Credential(
            name=credential.name,
            type=credential.type,
            encrypted_data=encrypted_data,
            created_by_id=user_id,
            workspace_id=credential.workspace_id,
        )

        self.db.add(db_credential)
        self.db.commit()
        self.db.refresh(db_credential)
        return db_credential

    def update_credential(
        self, credential_id: UUID, credential: CredentialUpdate
    ) -> Optional[Credential]:
        """Update an existing credential."""
        db_credential = self.get_credential(credential_id)
        if not db_credential:
            return None

        # Update basic fields if provided
        if credential.name is not None:
            setattr(db_credential, "name", credential.name)

        # Update credential fields if provided
        if credential.fields is not None:
            # Validate the new fields
            validate_credential_fields(db_credential.type, credential.fields)
            # Encrypt the new fields
            encrypted_data = encrypt_credential_fields(credential.fields)
            setattr(db_credential, "encrypted_data", encrypted_data)

        self.db.commit()
        self.db.refresh(db_credential)
        return db_credential

    def delete_credential(self, credential_id: UUID) -> bool:
        """Delete a credential."""
        db_credential = self.get_credential(credential_id)
        if not db_credential:
            return False

        self.db.delete(db_credential)
        self.db.commit()
        return True

    def search(self, filters: Dict[str, Any]) -> List[Credential]:
        """
        Search credentials based on provided filters.

        Args:
            filters: Dictionary of filters where key is the field name and value is either:
                - A direct value (uses = operator)
                - A dictionary with 'operator' and 'value', e.g. {"operator": "ilike", "value": "%github%"}

        Returns:
            List[Credential]: List of credentials matching the filter criteria.
        """
        query = self.db.query(Credential)
        query = apply_filters(query, Credential, filters)
        return query.all()

    def get_credential_fields(self, credential_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get the decrypted fields of a credential.
        This should only be used in secure contexts where the actual credential values are needed.
        """
        db_credential = self.get_credential(credential_id)
        if not db_credential:
            return None

        try:
            encrypted_data = getattr(db_credential, "encrypted_data")
            return decrypt_credential_fields(encrypted_data)
        except Exception:
            return None

    def to_credential_info(self, credential: Credential) -> CredentialInfo:
        """Convert a Credential model to CredentialInfo with field information."""
        # Get the field definitions from the credential type
        type_info = credential_registry.get(credential.type)
        fields = {}

        if type_info:
            # Get the decrypted fields
            decrypted_fields = self.get_credential_fields(credential.id)

            if decrypted_fields:
                # Include all fields, but obfuscate sensitive ones
                fields = {
                    field.name: (
                        "[OBFUSCATED]"
                        if field.input_type in ["password", "textarea"]
                        else decrypted_fields.get(field.name)
                    )
                    for field in type_info.fields
                }

        # Create CredentialInfo with the fields
        return CredentialInfo(
            id=credential.id,
            name=credential.name,
            type=credential.type,
            workspace_id=credential.workspace_id,
            created_by=credential.created_by,
            created_at=credential.created_at,
            updated_at=credential.updated_at,
            fields=fields,
        )

    def apply_credentials(
        self,
        credential_id: UUID,
        headers: Optional[Dict[str, str]] = None,
        access_token: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Apply credentials to headers based on the credential type.

        Args:
            credential_id: The UUID of the credential to apply
            headers: Optional existing headers to merge with
            access_token: Optional access token to use for Identies Authentication. This is the request user token
        Returns:
            Dictionary of headers with authentication applied

        Raises:
            ValueError: If the credential type is not supported or required fields are missing
        """
        # Get the credential from the database
        credential = self.get_credential(credential_id)
        if not credential:
            raise ValueError(f"Credential with ID {credential_id} not found")

        # Get the decrypted fields
        credential_fields = self.get_credential_fields(credential_id)
        if not credential_fields:
            credential_fields = {}

        if headers is None:
            headers = {}

        headers = headers.copy()  # Create a copy to avoid modifying the input

        if credential.type == CredentialType.BEARER_AUTH:
            if "token" not in credential_fields:
                raise ValueError("Bearer auth requires a token field")
            headers["Authorization"] = f"Bearer {credential_fields['token']}"

        elif credential.type == CredentialType.BASIC_AUTH:
            if (
                "username" not in credential_fields
                or "password" not in credential_fields
            ):
                raise ValueError(
                    "Basic auth requires both username and password fields"
                )
            import base64

            auth_str = (
                f"{credential_fields['username']}:{credential_fields['password']}"
            )
            auth_bytes = auth_str.encode("ascii")
            base64_bytes = base64.b64encode(auth_bytes)
            headers["Authorization"] = f"Basic {base64_bytes.decode('ascii')}"

        elif credential.type == CredentialType.GITHUB_PAT:
            if "token" not in credential_fields:
                raise ValueError("GitHub PAT requires a token field")
            headers["Authorization"] = f"Bearer {credential_fields['token']}"

        elif credential.type == CredentialType.GITLAB_PAT:
            if "token" not in credential_fields:
                raise ValueError("GitLab PAT requires a token field")
            headers["Authorization"] = f"Bearer {credential_fields['token']}"

        elif credential.type == CredentialType.IDENTIES_AUTH:
            if access_token is None:
                raise ValueError("Identies auth requires an access token")
            headers["Authorization"] = f"Bearer {access_token}"

        # SSH_KEY type is not applicable for HTTP headers

        return headers
