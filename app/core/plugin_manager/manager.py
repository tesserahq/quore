from typing import Optional, cast
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.mcp_client import MCPClient
from app.models.plugin import Plugin
from app.schemas.plugin import PluginUpdate
from app.services.credential import CredentialService
from app.constants.plugin_states import PluginState


class PluginManager:
    """Manages plugin lifecycle including downloading, inspecting, starting, and stopping."""

    def __init__(
        self,
        db: Session,
        plugin_id: Optional[UUID] = None,
        plugin: Optional[Plugin] = None,
        access_token: Optional[str] = None,
    ):
        """Initialize the plugin manager with a database session and plugin ID."""
        self.db = db
        self.access_token = access_token
        from app.services.plugin import PluginService

        self.plugin_service = PluginService(db)
        if plugin_id:
            self.plugin = self.plugin_service.get_plugin(plugin_id)
        elif plugin:
            self.plugin = plugin

        # Initialize services
        self.credential_service = CredentialService(db)

    def _get_credential_fields(self) -> Optional[dict]:
        """Get decrypted credential fields if a credential is set."""
        if not self.plugin.credential_id:
            return None

        return self.credential_service.get_credential_fields(
            cast(UUID, self.plugin.credential_id)
        )

    async def _build_mcp_client(self) -> MCPClient:
        """Build and return an MCP client with appropriate credentials."""
        headers = None
        if self.plugin.credential_id:
            headers = self.credential_service.apply_credentials(
                cast(UUID, self.plugin.credential_id), access_token=self.access_token
            )

        return MCPClient(str(self.plugin.endpoint_url), headers=headers)

    async def refresh(self) -> Plugin:
        """Refresh and update all plugin components (tools, resources, prompts) from the MCP server."""
        try:
            async with await self._build_mcp_client() as client:
                tools = []
                if client.tools_enabled():
                    tools = await client.list_tools()

                resources = []
                if client.resource_enabled():
                    resources = await client.list_resources()

                prompts = []
                if client.prompt_enabled():
                    prompts = await client.list_prompts()

            # Convert Tool objects to dictionaries
            tools_dicts = [tool.__dict__ for tool in tools]
            resources_dicts = [resource.__dict__ for resource in resources]
            prompts_dicts = [prompt.__dict__ for prompt in prompts]

            return self.plugin_service.update_plugin(
                cast(UUID, self.plugin.id),
                PluginUpdate(
                    name=str(self.plugin.name),
                    state=PluginState.RUNNING,
                    tools=tools_dicts,
                    resources=resources_dicts,
                    prompts=prompts_dicts,
                    state_description="Plugin components refreshed successfully",
                ),
            )
        except Exception as e:
            return self.plugin_service.update_plugin(
                cast(UUID, self.plugin.id),
                PluginUpdate(
                    name=str(self.plugin.name),
                    state=PluginState.ERROR,
                    state_description=f"Failed to refresh plugin components: {str(e)}",
                ),
            )

    async def get_tools(self):
        """Get the tools for the plugin."""
        async with await self._build_mcp_client() as client:
            return await client.list_tools()

    async def get_resources(self):
        """Get the resources for the plugin."""
        async with await self._build_mcp_client() as client:
            return await client.list_resources()

    async def get_prompts(self):
        """Get the prompts for the plugin."""
        async with await self._build_mcp_client() as client:
            return await client.list_prompts()
