from typing import Optional, cast, Any
from uuid import UUID
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.mcp_client import MCPClient
from app.models.plugin import Plugin
from app.schemas.plugin import PluginUpdate
from app.services.credential_service import CredentialService
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
        from app.services.plugin_service import PluginService

        self.plugin_service = PluginService(db)
        if plugin_id:
            self.plugin = self.plugin_service.get_plugin(plugin_id)
        elif plugin:
            self.plugin = plugin

        # Initialize services
        self.credential_service = CredentialService(db)

    def _serialize_to_dict(self, obj: Any) -> Any:
        """Recursively serialize objects to JSON-serializable dictionaries.

        Handles Pydantic models, AnyUrl types, and nested structures.

        Args:
            obj: The object to serialize

        Returns:
            JSON-serializable representation of the object
        """
        # Handle Pydantic models
        if isinstance(obj, BaseModel):
            return obj.model_dump(mode="json")

        # Handle Pydantic URL types (AnyUrl, Url, etc.)
        # Check by type name to handle different Pydantic URL implementations
        if hasattr(obj, "__class__"):
            class_name = obj.__class__.__name__
            if "Url" in class_name or "url" in class_name.lower():
                return str(obj)

        # Handle dictionaries - recursively process values
        if isinstance(obj, dict):
            return {key: self._serialize_to_dict(value) for key, value in obj.items()}

        # Handle lists and tuples - recursively process items
        if isinstance(obj, (list, tuple)):
            return [self._serialize_to_dict(item) for item in obj]

        # Handle objects with __dict__ attribute
        if hasattr(obj, "__dict__"):
            return self._serialize_to_dict(obj.__dict__)

        # Return primitive types as-is
        return obj

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

            # Convert objects to JSON-serializable dictionaries
            tools_dicts = [self._serialize_to_dict(tool) for tool in tools]
            resources_dicts = [
                self._serialize_to_dict(resource) for resource in resources
            ]
            prompts_dicts = [self._serialize_to_dict(prompt) for prompt in prompts]

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
