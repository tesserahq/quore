from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, Query
from app.constants.plugin_states import PluginState
from app.models.plugin import Plugin
from app.models.project_plugin import ProjectPlugin
from app.models.project import Project
from app.schemas.plugin import PluginCreate, PluginUpdate
from app.services.soft_delete_service import SoftDeleteService


class PluginService(SoftDeleteService[Plugin]):
    """Service for managing plugin registration and configuration."""

    def __init__(self, db: Session):
        super().__init__(db, Plugin)

    def update_state(self, plugin_id: UUID, state: PluginState) -> Plugin:
        """Update the state of a plugin."""
        plugin = self.get_plugin(plugin_id)
        plugin.state = state
        self.db.commit()
        self.db.refresh(plugin)
        return plugin

    def create_plugin(self, plugin_data: PluginCreate) -> Plugin:
        """Register a new plugin in the system."""
        # Create plugin with INITIALIZING state
        plugin = Plugin(**plugin_data.model_dump())
        plugin.state = PluginState.INITIALIZING
        self.db.add(plugin)
        self.db.commit()
        self.db.refresh(plugin)

        return plugin

    def find_plugin(self, plugin_id: UUID) -> Optional[Plugin]:
        """Find a plugin by ID. Returns None if not found."""
        return self.db.query(Plugin).filter(Plugin.id == plugin_id).first()

    def get_plugin(self, plugin_id: UUID) -> Plugin:
        """Get a plugin by ID. Raises ValueError if not found."""
        plugin = self.find_plugin(plugin_id)
        if plugin is None:
            raise ValueError(f"Plugin with ID {plugin_id} not found")
        return plugin

    def update_plugin(self, plugin_id: UUID, plugin_data: PluginUpdate) -> Plugin:
        """Update plugin metadata."""
        plugin = self.get_plugin(plugin_id)
        update_data = plugin_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(plugin, key, value)
        self.db.commit()
        self.db.refresh(plugin)
        return plugin

    def delete_plugin(self, plugin_id: UUID) -> bool:
        """Soft delete a plugin and all its configurations."""
        return self.delete_record(plugin_id)

    # Workspace Plugin Management
    def get_workspace_plugins(self, workspace_id: UUID) -> List[Plugin]:
        """Get all plugins for a workspace."""
        return self.db.query(Plugin).filter(Plugin.workspace_id == workspace_id).all()

    def get_workspace_plugins_query(self, workspace_id: UUID) -> Query:
        """Get a query for plugins in a workspace.

        Args:
            workspace_id: The UUID of the workspace

        Returns:
            Query: SQLAlchemy query for plugins in the workspace
        """
        return self.db.query(Plugin).filter(Plugin.workspace_id == workspace_id)

    def get_global_workspace_plugins(self, workspace_id: UUID) -> List[Plugin]:
        """Get all global plugins for a workspace."""
        return (
            self.db.query(Plugin)
            .filter(
                Plugin.workspace_id == workspace_id, Plugin.is_enabled, Plugin.is_global
            )
            .all()
        )

    # Project Plugin Management
    def enable_plugin_in_project(
        self,
        project_id: UUID,
        plugin_id: UUID,
        is_enabled: bool,
        tools: List[Dict[str, Any]],
        resources: List[Dict[str, Any]],
        prompts: List[Dict[str, Any]],
    ) -> ProjectPlugin:
        """
        Enable a plugin in a project.
        If the plugin is already installed, update its configuration and ensure it's enabled.
        """
        plugin = self.get_plugin(plugin_id)
        if plugin.is_global:
            raise ValueError("Global plugins cannot be enabled in a project")

        # Check if plugin is already installed
        project_plugin = (
            self.db.query(ProjectPlugin)
            .filter(
                ProjectPlugin.project_id == project_id,
                ProjectPlugin.plugin_id == plugin_id,
            )
            .first()
        )

        if project_plugin:
            # Update existing plugin
            project_plugin.is_enabled = is_enabled
            if tools is not None:
                project_plugin.tools = tools
            if resources is not None:
                project_plugin.resources = resources
            if prompts is not None:
                project_plugin.prompts = prompts
            self.db.commit()
            self.db.refresh(project_plugin)
            return project_plugin

        # Create new plugin installation
        project_plugin = ProjectPlugin(
            project_id=project_id,
            plugin_id=plugin_id,
            is_enabled=is_enabled,
            tools=tools or [],
            resources=resources or [],
            prompts=prompts or [],
        )
        self.db.add(project_plugin)
        self.db.commit()
        self.db.refresh(project_plugin)
        return project_plugin

    def disable_plugin_in_project(self, project_id: UUID, plugin_id: UUID) -> bool:
        """Disable a plugin in a project."""
        project_plugin = (
            self.db.query(ProjectPlugin)
            .filter(
                ProjectPlugin.project_id == project_id,
                ProjectPlugin.plugin_id == plugin_id,
            )
            .first()
        )
        if project_plugin:
            project_plugin.is_enabled = False
            self.db.commit()
            return True
        return False

    def get_project_plugins(self, project_id: UUID) -> List[Plugin]:
        """Get all enabled plugins for a project."""
        project = self.db.query(Project).filter(Project.id == project_id).first()

        if not project:
            return []

        # Get all plugins from the project's workspace
        global_workspace_plugins = self.get_global_workspace_plugins(
            project.workspace_id
        )

        # Get project-specific plugin configurations
        project_plugins = (
            self.db.query(Plugin)
            .join(ProjectPlugin, ProjectPlugin.plugin_id == Plugin.id)
            .filter(ProjectPlugin.project_id == project_id, ProjectPlugin.is_enabled)
            .all()
        )

        # Combine plugins and remove duplicates based on plugin ID
        all_plugins = {}

        # Add global plugins first
        for plugin in global_workspace_plugins:
            all_plugins[plugin.id] = plugin

        # Add project plugins (will override global plugins if same ID)
        for plugin in project_plugins:
            all_plugins[plugin.id] = plugin

        return list(all_plugins.values())

    def get_project_tools(self, project_id: UUID) -> List[Dict[str, Any]]:
        """Get all enabled plugins for a project."""
        plugins = self.get_project_plugins(project_id)
        # Flatten the list of tools from all plugins, handling None values
        all_tools: List[Dict[str, Any]] = []
        for plugin in plugins:
            if plugin.tools is not None:
                all_tools.extend(plugin.tools)
        return all_tools
