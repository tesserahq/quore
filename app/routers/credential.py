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
    CredentialTypeInfo,
)
from app.services.credential_service import CredentialService
from app.schemas.common import ListResponse
from app.utils.auth import get_current_user
from app.models.workspace import Workspace
from app.models.credential import Credential
from app.routers.utils.dependencies import get_workspace_by_id
from app.core.credentials import credential_registry
from app.core.logging_config import get_logger
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

logger = get_logger()

# Workspace-scoped router
workspace_router = APIRouter(
    prefix="/workspaces/{workspace_id}/credentials", tags=["credentials"]
)

# Direct credential access router
credential_router = APIRouter(prefix="/credentials", tags=["credentials"])


@workspace_router.get("/types", response_model=List[CredentialTypeInfo])
def list_credential_types():
    """List all available credential types and their field schemas."""
    return list(credential_registry.values())


def get_credential_direct(
    credential_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Credential:
    """Get a credential directly by ID, checking user permissions."""
    logger.info(f"Getting credential {credential_id} for user {current_user.id}")

    credential_service = CredentialService(db)
    credential = credential_service.get_credential(credential_id)
    if credential is None:
        logger.warning(f"Credential {credential_id} not found")
        raise HTTPException(status_code=404, detail="Credential not found")

    # Check if user has access to the workspace containing this credential
    user_workspace_ids = [m.workspace_id for m in current_user.memberships]
    if credential.workspace_id not in user_workspace_ids:
        logger.warning(
            f"User {current_user.id} attempted to access credential {credential_id} from unauthorized workspace {credential.workspace_id}"
        )
        raise HTTPException(
            status_code=403, detail="Not authorized to access this credential"
        )

    return credential


@workspace_router.get("", response_model=Page[CredentialInfo])
def list_workspace_credentials(
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List credentials in a workspace."""
    credential_service = CredentialService(db)
    query = credential_service.get_workspace_credentials_query(workspace.id)
    page = paginate(db, query)

    # Transform Credential items to CredentialInfo
    transformed_items = [
        credential_service.to_credential_info(item) for item in page.items
    ]

    # Create a new Page with transformed items
    return Page(
        items=transformed_items,
        total=page.total,
        page=page.page,
        size=page.size,
        pages=page.pages,
    )


@workspace_router.post(
    "", response_model=CredentialInfo, status_code=status.HTTP_201_CREATED
)
def create_workspace_credential(
    credential_request: CredentialCreateRequest,
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new credential in a workspace."""
    credential = CredentialCreate(
        **credential_request.model_dump(), workspace_id=UUID(str(workspace.id))
    )
    credential_service = CredentialService(db)
    created_credential = credential_service.create_credential(
        credential, current_user.id
    )
    return credential_service.to_credential_info(created_credential)


@credential_router.get("/{credential_id}", response_model=CredentialInfo)
def get_credential(
    credential: Credential = Depends(get_credential_direct),
    db: Session = Depends(get_db),
):
    """Get a specific credential by ID."""
    return CredentialService(db).to_credential_info(credential)


@credential_router.put("/{credential_id}", response_model=CredentialInfo)
def update_credential(
    credential_update: CredentialUpdate,
    credential: Credential = Depends(get_credential_direct),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a credential by ID."""
    updated_credential = CredentialService(db).update_credential(
        UUID(str(credential.id)), credential_update
    )
    return updated_credential


@credential_router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_credential(
    credential: Credential = Depends(get_credential_direct),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a credential by ID."""
    success = CredentialService(db).delete_credential(UUID(str(credential.id)))
    if not success:
        raise HTTPException(status_code=404, detail="Credential not found")
    return


@credential_router.post(
    "", response_model=CredentialInfo, status_code=status.HTTP_201_CREATED
)
def create_credential(
    credential_request: CredentialCreateRequest,
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new credential."""
    # Check if user has access to the workspace
    if not any(m.workspace_id == workspace_id for m in current_user.memberships):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create credentials in this workspace",
        )

    credential = CredentialCreate(
        **credential_request.model_dump(), workspace_id=workspace_id
    )
    credential_service = CredentialService(db)
    created_credential = credential_service.create_credential(
        credential, current_user.id
    )
    return credential_service.to_credential_info(created_credential)
