import os
from uuid import UUID
from app.config import get_settings


class PathManager:
    """Manages all path-related operations for the application."""

    def __init__(self):
        self.settings = get_settings()

    def get_plugin_dir(self, workspace_id: UUID, plugin_id: UUID) -> str:
        """Get the directory path for a specific plugin."""
        return os.path.join(
            self.settings.plugins_dir, str(workspace_id), str(plugin_id)
        )

    def get_workspace_plugins_dir(self, workspace_id: UUID) -> str:
        """Get the directory path for all plugins in a workspace."""
        return os.path.join(self.settings.plugins_dir, str(workspace_id))

    def ensure_plugin_dir(self, workspace_id: UUID, plugin_id: UUID) -> str:
        """Ensure plugin directory exists and return its path."""
        plugin_dir = self.get_plugin_dir(workspace_id, plugin_id)
        os.makedirs(plugin_dir, exist_ok=True)
        return plugin_dir
