from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from app.models.workspace import Workspace
from app.models.project import Project
from app.models.prompt import Prompt
from app.models.plugin import Plugin
from app.models.credential import Credential
from app.constants.plugin_states import PluginState
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceStats,
    ProjectStats,
    ProjectSummary,
    PromptStats,
    PromptSummary,
    PluginStats,
    CredentialStats,
    CredentialSummary,
)
from app.utils.db.filtering import apply_filters
from app.services.workspace_prune import WorkspacePruneService
from app.services.soft_delete_service import SoftDeleteService
from app.exceptions.workspace_exceptions import WorkspaceLockedError

"""
Module providing the WorkspaceService class for managing Workspace entities.
Includes methods for CRUD operations and dynamic searching with flexible filters.
"""


class WorkspaceService(SoftDeleteService[Workspace]):
    def __init__(self, db: Session):
        super().__init__(db, Workspace)
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
        """Soft delete a workspace after pruning its resources."""
        # First check if workspace exists and is not locked
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return False

        if workspace.locked:
            raise WorkspaceLockedError(str(workspace_id))

        # First prune all workspace resources
        if not self.prune_service.prune_workspace(workspace_id):
            return False

        # Then soft delete the workspace
        return self.delete_record(workspace_id)

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

    def get_workspace_stats(self, workspace_id: UUID) -> Optional[WorkspaceStats]:
        """
        Get comprehensive statistics for a workspace with optimized queries.

        Args:
            workspace_id: UUID of the workspace to get stats for

        Returns:
            WorkspaceStats: Statistics for the workspace or None if workspace doesn't exist
        """
        # First verify the workspace exists
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return None

        # Count total projects
        total_projects = (
            self.db.query(func.count(Project.id))
            .filter(Project.workspace_id == workspace_id)
            .scalar()
        )

        # Count total prompts
        total_prompts = (
            self.db.query(func.count(Prompt.id))
            .filter(Prompt.workspace_id == workspace_id)
            .scalar()
        )

        # Get 5 most recently updated projects
        recent_projects_query = (
            self.db.query(Project)
            .filter(Project.workspace_id == workspace_id)
            .order_by(desc(Project.updated_at))
            .limit(5)
        )
        recent_projects = [
            ProjectSummary(
                id=p.id, name=p.name, description=p.description, updated_at=p.updated_at
            )
            for p in recent_projects_query.all()
        ]

        # Get 5 most recently updated prompts
        recent_prompts_query = (
            self.db.query(Prompt)
            .filter(Prompt.workspace_id == workspace_id)
            .order_by(desc(Prompt.updated_at))
            .limit(5)
        )
        recent_prompts = [
            PromptSummary(id=p.id, name=p.name, type=p.type, updated_at=p.updated_at)
            for p in recent_prompts_query.all()
        ]

        # Get plugin statistics (enabled vs disabled)
        # Consider RUNNING, IDLE, and STARTING as enabled
        # Consider STOPPED, ERROR, REGISTERED as disabled
        enabled_states = [PluginState.RUNNING, PluginState.IDLE, PluginState.STARTING]
        disabled_states = [
            PluginState.STOPPED,
            PluginState.ERROR,
            PluginState.REGISTERED,
            PluginState.INITIALIZING,
        ]

        plugin_stats_query = (
            self.db.query(
                func.count(case((Plugin.state.in_(enabled_states), 1))).label(
                    "enabled"
                ),
                func.count(case((Plugin.state.in_(disabled_states), 1))).label(
                    "disabled"
                ),
            )
            .filter(Plugin.workspace_id == workspace_id)
            .first()
        )

        plugin_stats = PluginStats(
            total_enabled=plugin_stats_query.enabled or 0,
            total_disabled=plugin_stats_query.disabled or 0,
        )

        # Count total credentials
        total_credentials = (
            self.db.query(func.count(Credential.id))
            .filter(Credential.workspace_id == workspace_id)
            .scalar()
        )

        # Get 5 most recently updated credentials
        recent_credentials_query = (
            self.db.query(Credential)
            .filter(Credential.workspace_id == workspace_id)
            .order_by(desc(Credential.updated_at))
            .limit(5)
        )
        recent_credentials = [
            CredentialSummary(
                id=c.id, name=c.name, type=c.type, updated_at=c.updated_at
            )
            for c in recent_credentials_query.all()
        ]

        credential_stats = CredentialStats(
            total_credentials=total_credentials or 0,
            recent_credentials=recent_credentials,
        )

        # Create project stats
        project_stats = ProjectStats(
            total_projects=total_projects or 0,
            recent_projects=recent_projects,
        )

        # Create prompt stats
        prompt_stats = PromptStats(
            total_prompts=total_prompts or 0,
            recent_prompts=recent_prompts,
        )

        return WorkspaceStats(
            project_stats=project_stats,
            prompt_stats=prompt_stats,
            plugin_stats=plugin_stats,
            credential_stats=credential_stats,
        )
