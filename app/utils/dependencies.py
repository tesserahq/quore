from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
from app.services.workspace import WorkspaceService
from app.models.workspace import Workspace


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