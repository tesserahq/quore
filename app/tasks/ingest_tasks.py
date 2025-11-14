from typing import Dict, Optional
from uuid import UUID

from app.core.celery_app import celery_app
from app.core.index_manager import IndexManager
from app.core.ingestor import Ingestor
from app.core.storage_manager import StorageManager
from app.db import SessionLocal
from app.exceptions.resource_not_found_error import ResourceNotFoundError
from app.models.project import Project


@celery_app.task
def ingest_project_text(
    project_id: str,
    ref_id: str,
    text: str,
    labels: Optional[Dict[str, str]] = None,
) -> None:
    """
    Background task to ingest raw text into a project's vector store.

    Args:
        project_id: ID of the project receiving the text.
        ref_id: Reference identifier for the text.
        text: The textual content to ingest.
        labels: Optional metadata labels to attach to the ingested text.
    """
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == UUID(project_id)).one_or_none()
        if project is None:
            raise ResourceNotFoundError(f"Project with id {project_id} not found")

        index_manager = IndexManager(db, project)
    finally:
        db.close()

    storage_manager = StorageManager()
    ingestor = Ingestor(
        index_manager.embedding_model(),
        storage_manager.vector_store(project),
    )
    ingestor.ingest_raw_text(ref_id, text, labels)
