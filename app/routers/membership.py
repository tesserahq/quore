from app.utils.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.db import get_db
from app.schemas.membership import (
    MembershipCreate,
    MembershipCreateRequest,
    MembershipInDB,
    MembershipUpdate,
    RolesResponse,
)
from app.services.membership_service import MembershipService
from app.schemas.common import ListResponse
from app.models.workspace import Workspace
from app.routers.utils.dependencies import get_workspace_by_id
from app.constants.membership import ROLES_DATA

workspace_membership_router = APIRouter(
    prefix="/workspaces/{workspace_id}/memberships", tags=["memberships"]
)

membership_router = APIRouter(prefix="/memberships", tags=["memberships"])


@workspace_membership_router.get("", response_model=ListResponse[MembershipInDB])
def list_memberships(
    skip: int = 0,
    limit: int = 100,
    workspace: Optional[Workspace] = Depends(get_workspace_by_id),
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List memberships with optional filtering by workspace or user."""
    membership_service = MembershipService(db)

    if workspace:
        memberships = membership_service.get_workspace_memberships(
            UUID(str(workspace.id)), skip, limit
        )
    elif user_id:
        memberships = membership_service.get_user_memberships(user_id, skip, limit)
    else:
        # If no filters provided, return memberships for current user
        memberships = membership_service.get_user_memberships(
            current_user.id, skip, limit
        )

    return ListResponse(data=memberships)


@membership_router.get("/roles", response_model=RolesResponse)
def get_roles():
    """Get the list of available membership roles."""
    return RolesResponse(roles=ROLES_DATA)


@membership_router.get("/{membership_id}", response_model=MembershipInDB)
def get_membership(
    membership_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific membership by ID."""
    membership = MembershipService(db).get_membership(membership_id)

    if membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    return membership


@membership_router.put("/{membership_id}", response_model=MembershipInDB)
def update_membership(
    membership_id: UUID,
    membership: MembershipUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a membership's role."""
    updated_membership = MembershipService(db).update_membership(
        membership_id, membership
    )
    if updated_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    return updated_membership


@membership_router.delete("/{membership_id}")
def delete_membership(
    membership_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a membership."""
    success = MembershipService(db).delete_membership(membership_id)
    if not success:
        raise HTTPException(status_code=404, detail="Membership not found")
    return {"message": "Membership deleted successfully"}
