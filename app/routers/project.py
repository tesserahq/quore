from app.utils.auth import get_current_user
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    File,
    UploadFile,
    Form,
    status,
)
from fastapi.responses import JSONResponse
import httpx
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
import json

from app.db import get_db
from app.schemas.project import (
    ProjectUpdate,
    Project,
    ProjectSearchFilters,
    ProjectSearchResponse,
    NodeListResponse,
    NodeResponse,
)
from app.services.project_service import ProjectService
from app.models.project import Project as ProjectModel
from app.routers.utils.dependencies import (
    get_project_by_id,
    get_project_membership_by_id,
)
from app.config import get_settings
from app.services.project_membership_service import ProjectMembershipService
from app.schemas.project_membership import (
    ProjectMembershipUpdate,
    ProjectMembershipInDB,
    ProjectMembershipResponse,
)
from app.schemas.common import ListResponse
from app.models.project_membership import ProjectMembership
from app.core.index_manager import IndexManager
from app.services.node_service import NodeService

router = APIRouter(prefix="/projects", tags=["workspace-projects"])


@router.get("/{project_id}/nodes", response_model=NodeListResponse)
def nodes(
    project: ProjectModel = Depends(get_project_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project_service = ProjectService(db)
    node_service = NodeService(db)
    # project is provided by dependency already; use NodeService to fetch nodes
    nodes = node_service.get_nodes(project)
    node_responses = [node_service.build_node_response(n) for n in nodes]
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


@router.get(
    "/{project_id}/memberships", response_model=ListResponse[ProjectMembershipResponse]
)
def list_project_memberships(
    project: ProjectModel = Depends(get_project_by_id),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectMembershipService(db)
    memberships = service.get_memberships_by_project(UUID(str(project.id)), skip, limit)
    return ListResponse(data=memberships)


@router.get("/{project_id}", response_model=Project)
def get_project(
    project: ProjectModel = Depends(get_project_by_id),
    current_user=Depends(get_current_user),
):
    """Get a specific project by ID."""
    return project


@router.put("/{project_id}", response_model=Project)
def update_project(
    project_update: ProjectUpdate,
    project: ProjectModel = Depends(get_project_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update an existing project."""
    service = ProjectService(db)
    updated = service.update_project(UUID(str(project.id)), project_update)
    if updated is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated


@router.put(
    "/{project_id}/memberships/{membership_id}",
    response_model=ProjectMembershipInDB,
)
def update_project_membership(
    membership_update: ProjectMembershipUpdate,
    membership: ProjectMembership = Depends(get_project_membership_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectMembershipService(db)
    updated = service.update_project_membership(
        UUID(str(membership.id)), membership_update
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Project membership not found")
    return updated


@router.get(
    "/{project_id}/memberships/{membership_id}",
    response_model=ProjectMembershipResponse,
)
def get_project_membership(
    membership: ProjectMembership = Depends(get_project_membership_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectMembershipService(db)
    membership = service.get_project_membership(UUID(str(membership.id)))
    if membership is None:
        raise HTTPException(status_code=404, detail="Project membership not found")
    return membership


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project: ProjectModel = Depends(get_project_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a project."""
    service = ProjectService(db)
    success = service.delete_project(UUID(str(project.id)))
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}


@router.delete(
    "/{project_id}/memberships/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project_membership(
    membership: ProjectMembership = Depends(get_project_membership_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectMembershipService(db)
    success = service.delete_project_membership(UUID(str(membership.id)))
    if not success:
        raise HTTPException(status_code=404, detail="Project membership not found")


@router.post("/{project_id}/documents")
async def create_project_document(
    request: Request,
    project: ProjectModel = Depends(get_project_by_id),
    file: UploadFile = File(description="The file to upload"),
    name: Optional[str] = Form(None),
    labels: Optional[str] = Form(None),
    current_user=Depends(get_current_user),
):
    """
    Forward document upload request to Vaulta service
    """
    settings = get_settings()

    # Prepare the files and form data for forwarding
    files = {"file": (file.filename, file.file, file.content_type)}

    # Parse existing labels and add project/workspace IDs
    custom_labels = {
        "project_id": str(project.id),
        "workspace_id": str(project.workspace_id),
        "user_id": str(current_user.id),
    }

    merged_labels: dict[str, str]
    if labels:
        parsed = json.loads(labels)
        if not isinstance(parsed, dict):
            parsed = {}
        merged_labels = {**parsed, **custom_labels}
    else:
        merged_labels = custom_labels

    data = {"labels": json.dumps(merged_labels)}
    if name:
        data["name"] = name

    # Forward the request to Vaulta
    async with httpx.AsyncClient() as client:
        print(data)
        response = await client.post(
            f"{settings.vaulta_api_url}/documents",
            files=files,
            data=data,
            headers={"authorization": request.headers.get("authorization") or ""},
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)


@router.post("/{project_id}/documents/search")
async def search_project_documents(
    request: Request,
    project: ProjectModel = Depends(get_project_by_id),
    current_user=Depends(get_current_user),
):
    """
    Search documents from a project by querying Vaulta service
    """
    settings = get_settings()

    # Create the query to find documents with this project_id
    query = {"labels": {"project_id": str(project.id)}}

    # Forward the request to Vaulta
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.vaulta_api_url}/documents/search",
            json={"query": query},
            headers={"authorization": request.headers.get("authorization") or ""},
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)


@router.post("/{project_id}/index/reset")
def reset_project_index(
    project: ProjectModel = Depends(get_project_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Reset (clear) all records from the project's index table without dropping the table."""
    index_manager = IndexManager(db, project)
    index_manager.reset_index()
    return {"message": "Project index reset successfully"}
