from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.auth import get_current_user
from app.db import get_db
from app.services.project import ProjectService
from app.core.index_manager import IndexManager

router = APIRouter(prefix="/projects", tags=["projects"])


# Define a Pydantic model for the request body
class IngestTextRequest(BaseModel):
    id: str
    text: str
    labels: Optional[Dict[str, str]] = None


@router.post("/{project_id}/ingest/text", status_code=status.HTTP_200_OK)
def ingest_text(
    project_id: UUID,
    request: IngestTextRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Ingest raw text into the vector store for a specific project.

    Args:
        project_id (UUID): The ID of the project to ingest text into.
        request (IngestTextRequest): The request body containing text and labels.
        db (Session): The database session.
        current_user: The currently authenticated user.

    Returns:
        dict: A success message.
    """
    # Fetch the project
    project_service = ProjectService(db)
    project = project_service.get_project(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found.",
        )

    # Use IndexManager to ingest the text
    index_manager = IndexManager(db, project)
    index_manager.ingest_raw_text(request.id, request.text, request.labels)

    return {"message": "Text successfully ingested into the vector store."}
