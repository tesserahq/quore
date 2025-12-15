from app.models.membership import Membership
from app.services.workspace_service import WorkspaceService
from app.utils.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.db import get_db
from app.schemas.membership import (
    MembershipInDB,
    MembershipResponse,
    MembershipUpdate,
    RolesResponse,
)
from app.services.membership_service import MembershipService
from app.schemas.common import ListResponse
from app.models.workspace import Workspace
from app.routers.utils.dependencies import get_membership_by_id, get_workspace_by_id
from app.constants.membership import ROLES_DATA
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

workspace_membership_router = APIRouter(
    prefix="/workspaces/{workspace_id}/memberships", tags=["memberships"]
)

membership_router = APIRouter(prefix="/memberships", tags=["memberships"])


@workspace_membership_router.get("", response_model=Page[MembershipResponse])
def list_memberships(
    workspace: Optional[Workspace] = Depends(get_workspace_by_id),
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List memberships with optional filtering by workspace or user."""
    membership_service = MembershipService(db)

    if workspace:
        query = membership_service.get_memberships_by_workspace_query(
            UUID(str(workspace.id))
        )
    elif user_id:
        query = membership_service.get_user_memberships_query(user_id)
    else:
        # If no filters provided, return memberships for current user
        query = membership_service.get_user_memberships_query(current_user.id)

    return paginate(db, query)


@membership_router.get("/roles", response_model=RolesResponse)
def get_roles():
    """Get the list of available membership roles."""
    return RolesResponse(roles=ROLES_DATA)


@membership_router.get("/{membership_id}", response_model=MembershipResponse)
def get_membership(
    membership: Membership = Depends(get_membership_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific membership by ID."""
    return membership


@membership_router.put("/{membership_id}", response_model=MembershipInDB)
def update_membership(
    membership_data: MembershipUpdate,
    membership: Membership = Depends(get_membership_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a membership's role."""
    updated_membership = MembershipService(db).update_membership(
        membership.id, membership_data
    )
    if updated_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    return updated_membership


@membership_router.delete("/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_membership(
    membership: Membership = Depends(get_membership_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a membership."""
    # Get the workspace to check if this membership belongs to the workspace creator
    workspace_service = WorkspaceService(db)
    workspace = workspace_service.get_workspace(membership.workspace_id)

    if not workspace:
        raise HTTPException(status_code=404, detail="Account not found")

    # Prevent deleting the workspace owner's membership (original validation)
    if membership.user_id == workspace.created_by_id:
        raise HTTPException(
            status_code=400, detail="Cannot delete the workspace owner's membership"
        )

    # Use the service method that handles all validations
    membership_service = MembershipService(db)
    success = membership_service.delete_membership_with_validation(
        membership.id, current_user.id, membership.workspace_id
    )

    if not success:
        raise HTTPException(status_code=404, detail="Membership not found")
