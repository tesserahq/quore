import os
import shutil
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.logging_config import get_logger
from app.core.path_manager import PathManager

logger = get_logger()


class WorkspacePruneService:
    """Service for cleaning up workspace-related resources when a workspace is deleted."""

    def __init__(self, db: Session):
        self.db = db
        self.path_manager = PathManager()

    def prune_workspace(self, workspace_id: UUID) -> bool:
        """
        Clean up all resources associated with a workspace.
        This includes:
        - Plugin directories
        - Any other workspace-specific storage
        """
        try:
            # Get workspace directory path
            workspace_dir = self.path_manager.get_workspace_plugins_dir(workspace_id)

            # Remove workspace directory if it exists
            if os.path.exists(workspace_dir):
                shutil.rmtree(workspace_dir)
                logger.info(f"Removed workspace directory: {workspace_dir}")

            return True
        except Exception as e:
            logger.error(f"Error pruning workspace {workspace_id}: {str(e)}")
            return False
