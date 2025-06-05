import asyncio
from typing import Optional, cast, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.mcp_client import MCPClient
from app.services.credential import CredentialService
from app.config import get_settings
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
        self.credential_service = CredentialService(db)

        # Get settings
        settings = get_settings()

    def _get_credential_fields(self) -> Optional[dict]:
        """Get decrypted credential fields if a credential is set."""
        if not self.plugin.credential_id:
            return None

        return self.credential_service.get_credential_fields(
            cast(UUID, self.plugin.credential_id)
        )

    def inspect(self) -> None:
        """Inspect the plugin to determine its type and requirements."""
        if not self.plugin.endpoint_url:
            raise ValueError("Plugin endpoint URL is not set")

        async def inspect_plugin():
            # Create FastMCP client for the plugin's endpoint
            client = MCPClient(self.plugin.endpoint_url)

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
                        }
                        plugin_service.register_tool(self.plugin.id, tool_data)

            except Exception as e:
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
