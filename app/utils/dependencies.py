from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
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
