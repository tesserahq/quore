from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db import get_db
from app.schemas.credential import (
    CredentialInfo,
    CredentialCreate,
    CredentialCreateRequest,
    CredentialUpdate,
)
from app.services.credential import CredentialService
from app.services.workspace import WorkspaceService
from app.schemas.common import ListResponse
from app.utils.auth import get_current_user
from app.models.workspace import Workspace
from app.models.credential import Credential
from app.utils.dependencies import get_workspace_by_id

router = APIRouter(
    prefix="/workspaces/{workspace_id}/credentials", tags=["credentials"]
)


def get_credential_by_id(
    credential_id: UUID,
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
) -> Credential:
    credential = CredentialService(db).get_credential(credential_id)
    if credential is None or credential.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Credential not found")
    return credential


@router.get("", response_model=ListResponse[CredentialInfo])
def list_credentials(
    workspace: Workspace = Depends(get_workspace_by_id),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List credentials in a workspace."""
    filters = {"workspace_id": workspace.id}
    credentials = CredentialService(db).search(filters)
    return ListResponse(data=credentials)


@router.post("", response_model=CredentialInfo, status_code=status.HTTP_201_CREATED)
def create_credential(
    credential_request: CredentialCreateRequest,
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new credential in a workspace."""
    # Convert the request to a full CredentialCreate with workspace_id
    credential = CredentialCreate(
        **credential_request.model_dump(), workspace_id=UUID(str(workspace.id))
    )
    return CredentialService(db).create_credential(credential, current_user.id)


@router.get("/{credential_id}", response_model=CredentialInfo)
def get_credential(
    credential: Credential = Depends(get_credential_by_id),
):
    """Get a specific credential in a workspace."""
    return credential


@router.put("/{credential_id}", response_model=CredentialInfo)
def update_credential(
    credential_update: CredentialUpdate,
    credential: Credential = Depends(get_credential_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a credential in a workspace."""
    updated_credential = CredentialService(db).update_credential(
        UUID(str(credential.id)), credential_update
    )
    return updated_credential


@router.delete("/{credential_id}")
def delete_credential(
    credential: Credential = Depends(get_credential_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a credential from a workspace."""
    success = CredentialService(db).delete_credential(UUID(str(credential.id)))
    if not success:
        raise HTTPException(status_code=404, detail="Credential not found")
    return {"message": "Credential deleted successfully"}
