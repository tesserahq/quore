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
from app.routers.utils.dependencies import get_project_by_id
from app.config import get_settings

router = APIRouter(prefix="/projects", tags=["workspace-projects"])


@router.get("/{project_id}/nodes", response_model=NodeListResponse)
def nodes(
    project: ProjectModel = Depends(get_project_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectService(db)
    nodes = service.get_nodes(project_id=project.id)
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
    project: ProjectModel = Depends(get_project_by_id),
    current_user=Depends(get_current_user),
):
    """Get a specific project by ID."""
    return project


@router.put("/{project_id}", response_model=Project)
def update_project(
    project: ProjectModel = Depends(get_project_by_id),
    project_update: ProjectUpdate = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update an existing project."""
    service = ProjectService(db)
    updated = service.update_project(project.id, project_update)
    if updated is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project: ProjectModel = Depends(get_project_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a project."""
    service = ProjectService(db)
    success = service.delete_project(project.id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/documents")
async def create_project_document(
    file: UploadFile = File(description="The file to upload"),
    project: ProjectModel = Depends(get_project_by_id),
    request: Request = None,
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

    if labels:
        labels = json.loads(labels)
        labels.update(custom_labels)
    else:
        labels = custom_labels

    data = {"labels": json.dumps(labels)}
    if name:
        data["name"] = name

    # Forward the request to Vaulta
    async with httpx.AsyncClient() as client:
        print(data)
        response = await client.post(
            f"{settings.vaulta_api_url}/documents",
            files=files,
            data=data,
            headers={"authorization": request.headers.get("authorization")},
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)


@router.post("/{project_id}/documents/search")
async def search_project_documents(
    project: ProjectModel = Depends(get_project_by_id),
    request: Request = None,
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
            headers={"authorization": request.headers.get("authorization")},
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)
