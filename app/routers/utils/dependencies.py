from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
from app.models.credential import Credential
from app.models.invitation import Invitation
from app.models.plugin import Plugin
from app.services.credential import CredentialService
from app.services.invitation_service import InvitationService
from app.services.plugin import PluginService
from app.services.workspace import WorkspaceService
from app.models.workspace import Workspace
from app.services.project import ProjectService
from app.models.project import Project


def get_workspace_by_id(
    workspace_id: UUID,
    db: Session = Depends(get_db),
) -> Workspace:
    """FastAPI dependency to get a workspace by ID.

    Args:
        workspace_id: The UUID of the workspace to retrieve
        db: Database session dependency

    Returns:
        Workspace: The retrieved workspace

    Raises:
        HTTPException: If the workspace is not found
    """
    workspace = WorkspaceService(db).get_workspace(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


def get_project_by_id(
    project_id: UUID,
    db: Session = Depends(get_db),
) -> Project:
    """FastAPI dependency to get a project by ID.

    Args:
        project_id: The UUID of the project to retrieve
        db: Database session dependency

    Returns:
        Project: The retrieved project

    Raises:
        HTTPException: If the project is not found
    """
    project = ProjectService(db).get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def get_plugin_by_id(
    plugin_id: UUID,
    db: Session = Depends(get_db),
) -> Plugin:
    """FastAPI dependency to get a plugin by ID.

    Args:
        plugin_id: The UUID of the plugin to retrieve
        db: Database session dependency

    Returns:
        Plugin: The retrieved plugin

    Raises:
        HTTPException: If the plugin is not found
    """
    plugin = PluginService(db).get_plugin(plugin_id)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin


def get_access_token(
    authorization: str = Header(..., description="Authorization header"),
) -> str:
    """FastAPI dependency to get the access token from the authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Invalid authorization header format"
        )
    return authorization[7:]  # Remove "Bearer " prefix


def get_credential_by_id(
    credential_id: UUID,
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
) -> Credential:
    credential = CredentialService(db).get_credential(credential_id)
    if credential is None or credential.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Credential not found")
    return credential


def get_invitation_by_id(
    invitation_id: UUID,
    db: Session = Depends(get_db),
) -> Invitation:
    """FastAPI dependency to get an invitation by ID.

    Args:
        invitation_id: The UUID of the invitation to retrieve
        db: Database session dependency

    Returns:
        Invitation: The retrieved invitation

    Raises:
        HTTPException: If the invitation is not found
    """
    invitation = InvitationService(db).get_invitation(invitation_id)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    return invitation
