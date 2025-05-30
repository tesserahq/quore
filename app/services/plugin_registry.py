from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.constants.plugin_states import PluginState
from app.models.plugin import Plugin
from app.models.plugin_tool import PluginTool
from app.models.project_plugin import ProjectPlugin
from app.models.project_plugin_tool import ProjectPluginTool
from app.models.project import Project
from app.schemas.plugin import PluginCreate, PluginUpdate, PluginToolCreate


class PluginRegistryService:
    """Service for managing plugin registration and configuration."""

    def __init__(self, db: Session):
        self.db = db

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
        """Delete a plugin and all its configurations."""
        plugin = self.get_plugin(plugin_id)
        self.db.delete(plugin)
        self.db.commit()
        return True

    # Tool Management
    def register_tool(self, plugin_id: UUID, tool_data: PluginToolCreate) -> PluginTool:
        """Register a new tool for a plugin."""
        tool = PluginTool(plugin_id=plugin_id, **tool_data.model_dump())
        self.db.add(tool)
        self.db.commit()
        self.db.refresh(tool)
        return tool

    def get_plugin_tools(self, plugin_id: UUID) -> List[PluginTool]:
        """Get all tools for a plugin."""
        return self.db.query(PluginTool).filter(PluginTool.plugin_id == plugin_id).all()

    # Workspace Plugin Management
    def get_workspace_plugins(self, workspace_id: UUID) -> List[Plugin]:
        """Get all plugins for a workspace."""
        return self.db.query(Plugin).filter(Plugin.workspace_id == workspace_id).all()

    # Project Plugin Management
    def enable_plugin_in_project(
        self, project_id: UUID, plugin_id: UUID, config: Optional[Dict[str, Any]] = None
    ) -> ProjectPlugin:
        """
        Enable a plugin in a project.
        If the plugin is already installed, update its configuration and ensure it's enabled.
        """
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
            project_plugin.is_enabled = True
            if config is not None:
                project_plugin.config = config
            self.db.commit()
            self.db.refresh(project_plugin)
            return project_plugin

        # Create new plugin installation
        project_plugin = ProjectPlugin(
            project_id=project_id,
            plugin_id=plugin_id,
            is_enabled=True,
            config=config or {},
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
        workspace_plugins = self.get_workspace_plugins(project.workspace_id)

        # Get project-specific plugin configurations
        project_plugins = (
            self.db.query(ProjectPlugin)
            .filter(ProjectPlugin.project_id == project_id, ProjectPlugin.is_enabled)
            .all()
        )

        # Filter to only include enabled plugins
        enabled_plugin_ids = {pp.plugin_id for pp in project_plugins}
        return [p for p in workspace_plugins if p.id in enabled_plugin_ids]

    def get_enabled_tools_for_project(self, project_id: UUID) -> List[PluginTool]:
        """Get all enabled tools for a project."""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return []

        # Get all plugins from the project's workspace
        self.get_workspace_plugins(project.workspace_id)

        # Get project-specific plugin configurations
        project_plugins = (
            self.db.query(ProjectPlugin)
            .filter(ProjectPlugin.project_id == project_id, ProjectPlugin.is_enabled)
            .all()
        )

        # Get all tools from enabled plugins
        enabled_plugin_ids = {pp.plugin_id for pp in project_plugins}
        return (
            self.db.query(PluginTool)
            .filter(
                PluginTool.plugin_id.in_(enabled_plugin_ids),
                PluginTool.is_active,
            )
            .all()
        )

    def get_enabled_tools_for_workspace(self, workspace_id: UUID) -> List[PluginTool]:
        """Get all enabled tools for a workspace."""
        # Get all plugins from the workspace
        workspace_plugins = self.get_workspace_plugins(workspace_id)

        # Get all tools from workspace plugins
        workspace_plugin_ids = {p.id for p in workspace_plugins}
        return (
            self.db.query(PluginTool)
            .filter(
                PluginTool.plugin_id.in_(workspace_plugin_ids),
                PluginTool.is_active,
            )
            .all()
        )

    def update_tool_config(
        self, tool_id: UUID, config: Dict[str, Any], project_id: Optional[UUID] = None
    ) -> bool:
        """Update tool configuration for a project."""
        if project_id:
            project_tool = (
                self.db.query(ProjectPluginTool)
                .filter(
                    ProjectPluginTool.tool_id == tool_id,
                    ProjectPluginTool.project_plugin_id.in_(
                        self.db.query(ProjectPlugin.id).filter(
                            ProjectPlugin.project_id == project_id
                        )
                    ),
                )
                .first()
            )
            if project_tool:
                project_tool.config = config
                self.db.commit()
                return True
        return False

    def enable_tool_in_project(
        self, project_id: UUID, tool_id: UUID
    ) -> ProjectPluginTool:
        """Enable a tool in a project by creating a ProjectPluginTool record."""
        project_plugin = (
            self.db.query(ProjectPlugin)
            .filter(ProjectPlugin.project_id == project_id, ProjectPlugin.is_enabled)
            .first()
        )
        if not project_plugin:
            raise ValueError("Project plugin not found or not enabled")
        project_tool = ProjectPluginTool(
            project_plugin_id=project_plugin.id,
            tool_id=tool_id,
            is_enabled=True,
            config={},
        )
        self.db.add(project_tool)
        self.db.commit()
        self.db.refresh(project_tool)
        return project_tool
