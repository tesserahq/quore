from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.ingest_text_request import IngestTextRequest
from app.utils.auth import get_current_user
from app.db import get_db
from app.routers.utils.dependencies import get_project_by_id
from app.tasks.ingest_tasks import ingest_project_text

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/{project_id}/ingest/text", status_code=status.HTTP_200_OK)
def ingest_text(
    request: IngestTextRequest,
    db: Session = Depends(get_db),
    project: Project = Depends(get_project_by_id),
    current_user=Depends(get_current_user),
):
    """
    Ingest raw text into the vector store for a specific project.

    Args:
        request (IngestTextRequest): The request body containing text and labels.
        db (Session): The database session.
        project (Project): The project to ingest text into.
        current_user: The currently authenticated user.

    Returns:
        dict: A success message.
    """

    task = ingest_project_text.delay(
        str(project.id), request.ref_id, request.text, request.labels
    )

    return {
        "data": {
            "task_id": task.id,
            "status": "queued",
            "detail": "Text ingestion scheduled.",
        }
    }
