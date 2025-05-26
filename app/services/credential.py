from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.credential import Credential
from app.schemas.credential import CredentialCreate, CredentialUpdate, CredentialInfo
from app.utils.db.filtering import apply_filters
from app.core.credentials import (
    validate_credential_fields,
    encrypt_credential_fields,
    decrypt_credential_fields,
)


class CredentialService:
    def __init__(self, db: Session):
        self.db = db

    def get_credential(self, credential_id: UUID) -> Optional[Credential]:
        """Get a credential by its ID."""
        return self.db.query(Credential).filter(Credential.id == credential_id).first()

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
