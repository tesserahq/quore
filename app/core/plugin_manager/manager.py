import os
import subprocess
import asyncio
from typing import Optional, cast, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from fastmcp import Client

from app.core.credentials import apply_git_credentials
from app.services.credential import CredentialService
from app.config import get_settings
from app.core.path_manager import PathManager
from app.services.plugin_registry import PluginRegistryService
from app.constants.plugin_states import PluginState


class PluginManager:
    """Manages plugin lifecycle including downloading, inspecting, starting, and stopping."""

    def __init__(self, db: Session, plugin_id: UUID):
        """Initialize the plugin manager with a database session and plugin ID."""
        self.db = db
        from app.services.plugin_registry import PluginRegistryService

        plugin_service = PluginRegistryService(db)
        plugin = plugin_service.get_plugin(plugin_id)
        if not plugin:
            raise ValueError(f"Plugin with ID {plugin_id} not found")
        self.plugin = plugin  # Now we know it's not None

        # Initialize services
        self.path_manager = PathManager()
        self.credential_service = CredentialService(db)

        # Get plugin directory
        self.plugin_dir = self.path_manager.get_plugin_dir(
            cast(UUID, self.plugin.workspace_id), cast(UUID, self.plugin.id)
        )

        # Get settings
        settings = get_settings()

        # Base directory for plugin storage
        self.plugins_dir = settings.plugins_dir

    def _get_credential_fields(self) -> Optional[dict]:
        """Get decrypted credential fields if a credential is set."""
        if not self.plugin.credential_id:
            return None

        return self.credential_service.get_credential_fields(
            cast(UUID, self.plugin.credential_id)
        )

    def _prepare_git_command(self, repo_url: str) -> tuple[list[str], dict]:
        """Prepare git command and environment based on repository URL and credentials."""
        cred_fields = self._get_credential_fields() or {}
        cmd, env = apply_git_credentials(repo_url, cred_fields)
        # Add the target directory to the command
        cmd.append(self.plugin_dir)
        return cmd, env

    def clone_repository(self) -> None:
        """Clone the plugin repository and checkout the specified version."""
        if not self.plugin.repository_url:
            raise ValueError("Plugin repository URL is not set")

        # Remove existing repository if it exists
        if os.path.exists(self.plugin_dir):
            import shutil

            shutil.rmtree(self.plugin_dir)

        # Clone the repository
        cmd, env = self._prepare_git_command(str(self.plugin.repository_url))
        try:
            subprocess.run(cmd, env=env, check=True)

            # # Checkout specific version if specified
            # if self.plugin.version or self.plugin.commit_hash:
            #     os.chdir(self.plugin_dir)
            #     checkout_ref = self.plugin.version or self.plugin.commit_hash
            #     subprocess.run(["git", "checkout", checkout_ref], check=True)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to download plugin: {str(e)}")
        finally:
            # Clean up temporary key file if it was created
            if "GIT_SSH_COMMAND" in env:
                key_path = env["GIT_SSH_COMMAND"].split()[1]
                if os.path.exists(key_path):
                    os.unlink(key_path)

    def inspect(self) -> None:
        """Inspect the plugin to determine its type and requirements."""
        if not self.plugin.endpoint_url:
            raise ValueError("Plugin endpoint URL is not set")

        async def inspect_plugin():
            # Create FastMCP client for the plugin's endpoint
            client = Client(self.plugin.endpoint_url)

            try:
                async with client:
                    # Get available tools from the plugin
                    tools = await client.list_tools()

                    # Register each tool with the plugin
                    plugin_service = PluginRegistryService(self.db)
                    for tool in tools:
                        # Convert FastMCP tool to PluginToolCreate schema
                        tool_data = {
                            "name": tool.name,
                            "description": tool.description,
                            "is_active": True,
                            "input_schema": tool.input_schema,
                            "output_schema": tool.output_schema,
                            "tool_metadata": {
                                "mcp_version": "2.0",
                                "transport": "streamable-http",
                            },
                        }
                        plugin_service.register_tool(self.plugin.id, tool_data)

                    # Update plugin state to indicate successful inspection
                    self.plugin.state = PluginState.READY
                    self.db.commit()

            except Exception as e:
                # Update plugin state to indicate inspection failure
                self.plugin.state = PluginState.ERROR
                self.db.commit()
                raise RuntimeError(f"Failed to inspect plugin: {str(e)}")

        # Run the async inspection
        asyncio.run(inspect_plugin())

    def start(self) -> None:
        """Start the plugin server."""
        # TODO: Implement plugin startup
        pass

    def stop(self) -> None:
        """Stop the plugin server."""
        # TODO: Implement plugin shutdown
        pass
