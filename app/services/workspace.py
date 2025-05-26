from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.utils.db.filtering import apply_filters
from app.services.workspace_prune import WorkspacePruneService

"""
Module providing the WorkspaceService class for managing Workspace entities.
Includes methods for CRUD operations and dynamic searching with flexible filters.
"""


class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db
        self.prune_service = WorkspacePruneService(db)

    def get_workspace(self, workspace_id: UUID) -> Optional[Workspace]:
        return self.db.query(Workspace).filter(Workspace.id == workspace_id).first()

    def get_workspaces(self, skip: int = 0, limit: int = 100) -> List[Workspace]:
        return self.db.query(Workspace).offset(skip).limit(limit).all()

    def create_workspace(self, workspace: WorkspaceCreate) -> Workspace:
        db_workspace = Workspace(**workspace.model_dump())
        self.db.add(db_workspace)
        self.db.commit()
        self.db.refresh(db_workspace)
        return db_workspace

    def update_workspace(
        self, workspace_id: UUID, workspace: WorkspaceUpdate
    ) -> Optional[Workspace]:
        db_workspace = (
            self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
        )
        if db_workspace:
            update_data = workspace.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_workspace, key, value)
            self.db.commit()
            self.db.refresh(db_workspace)
        return db_workspace

    def delete_workspace(self, workspace_id: UUID) -> bool:
        db_workspace = (
            self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
        )
        if db_workspace:
            # First prune all workspace resources
            if not self.prune_service.prune_workspace(workspace_id):
                return False

            # Then delete the workspace from the database
            self.db.delete(db_workspace)
            self.db.commit()
            return True
        return False

    def search(self, filters: Dict[str, Any]) -> List[Workspace]:
        """
        Search workspaces based on provided filters.

        Args:
            filters: Dictionary of filters where key is the field name and value is either:
                - A direct value (uses = operator)
                - A dictionary with 'operator' and 'value', e.g. {"operator": "ilike", "value": "%john%"}

        Returns:
            List[Workspace]: List of workspaces matching the filter criteria.

        Example:
            filters = {
                "name": {"operator": "ilike", "value": "%john%"},
                "email": {"operator": "!=", "value": "test@example.com"},
                "is_active": True,
                "role": {"operator": "in", "value": ["admin", "user"]}
            }
        """
        query = self.db.query(Workspace)
        query = apply_filters(query, Workspace, filters)
        return query.all()
