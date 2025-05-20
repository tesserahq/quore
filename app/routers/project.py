from app.utils.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
from app.schemas.project import (
    ProjectUpdate,
    Project,
    ProjectSearchFilters,
    ProjectSearchResponse,
    NodeListResponse,
    NodeResponse,
)
from app.services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["workspace-projects"])


@router.get("/{project_id}/nodes", response_model=NodeListResponse)
def nodes(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectService(db)
    nodes = service.get_nodes(project_id=project_id)
    node_responses = []
    for node in nodes:
        node_dict = node.__dict__.copy()
        # Ensure metadata_ is a dict or None
        if (
            not isinstance(node_dict.get("metadata_"), dict)
            and node_dict.get("metadata_") is not None
        ):
            node_dict["metadata_"] = None
        node_responses.append(NodeResponse.model_validate(node_dict))
    return NodeListResponse(data=node_responses)


@router.post("/search", response_model=ProjectSearchResponse)
def search_projects(
    filters: ProjectSearchFilters,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Search projects based on provided filters.

    Each filter field can be either:
    - A direct value (e.g., "name": "Project 1")
    - A search operator object with:
        - operator: One of "=", "!=", ">", "<", ">=", "<=", "ilike", "in", "not in"
        - value: The value to compare against

    Example:
    {
        "name": {"operator": "ilike", "value": "%test%"},
        "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
        "llm_provider": "openai"
    }
    """
    service = ProjectService(db)
    results = service.search(filters.model_dump(exclude_none=True))
    return ProjectSearchResponse(data=results)


@router.get("/{project_id}", response_model=Project)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific project by ID."""
    service = ProjectService(db)
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: UUID,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update an existing project."""
    service = ProjectService(db)
    updated = service.update_project(project_id, project)
    if updated is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated


@router.delete("/{project_id}")
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a project."""
    service = ProjectService(db)
    success = service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}
