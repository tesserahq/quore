from app.schemas.project import ProjectCreate, Project
from app.services.project import ProjectService
from app.utils.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.workspace import Workspace, WorkspaceCreate, WorkspaceUpdate
from app.services.workspace import WorkspaceService
from app.schemas.common import ListResponse
from app.utils.dependencies import get_workspace_by_id

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=ListResponse[Workspace])
def list_workspaces(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {"created_by_id": current_user.id}
    workspaces = WorkspaceService(db).search(filters)
    return ListResponse(data=workspaces)


@router.post("", response_model=Workspace, status_code=status.HTTP_201_CREATED)
def create_workspace(
    workspace: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    workspace.created_by_id = current_user.id
    return WorkspaceService(db).create_workspace(workspace)


@router.get("/{workspace_id}", response_model=Workspace)
def get_workspace(workspace: Workspace = Depends(get_workspace_by_id)):
    return workspace


@router.put("/{workspace_id}", response_model=Workspace)
def update_workspace(
    workspace_update: WorkspaceUpdate,
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
):
    updated_workspace = WorkspaceService(db).update_workspace(
        workspace.id, workspace_update
    )

    return updated_workspace


@router.delete("/{workspace_id}")
def delete_workspace(
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
):
    success = WorkspaceService(db).delete_workspace(workspace.id)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"message": "Workspace deleted successfully"}


@router.get("/{workspace_id}/projects", response_model=ListResponse[Project])
def list_projects(
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List projects in a workspace."""
    service = ProjectService(db)

    # TODO: we need to filter by the user's membership in the workspace
    filters = {
        "workspace_id": {"operator": "=", "value": workspace.id},
    }

    projects = service.search(filters)
    return ListResponse(data=projects)


@router.post(
    "/{workspace_id}/projects",
    response_model=Project,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project: ProjectCreate,
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new project in a workspace."""
    service = ProjectService(db)

    # Override the workspace_id in the payload for safety
    project.workspace_id = workspace.id
    return service.create_project(project)
