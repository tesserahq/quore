from typing import List, Dict, Any, Optional
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from dataclasses import dataclass, field
from typing import Optional as Opt


@dataclass
class LoggingCapability:
    enabled: bool = True


@dataclass
class ResourcesCapability:
    subscribe: bool
    listChanged: bool


@dataclass
class ToolsCapability:
    listChanged: bool


@dataclass
class ServerCapabilities:
    experimental: Opt[Any] = None
    logging: LoggingCapability = field(default_factory=LoggingCapability)
    prompts: Opt[Any] = None
    resources: Opt[ResourcesCapability] = None
    tools: Opt[ToolsCapability] = None


class MCPClient:
    """A wrapper around the FastMCP client to provide a clean interface and allow for future implementation changes."""

    def __init__(self, endpoint_url: str, headers: Optional[Dict[str, str]] = None):
        """Initialize the MCP client with the given endpoint URL.

        Args:
            endpoint_url (str): The URL of the MCP server endpoint
            headers (Optional[Dict[str, str]]): Optional headers to pass to the client
        """
        self.endpoint_url = endpoint_url
        # self._client: FastMCPClient = FastMCPClient(
        #     endpoint_url, auth=headers.get("Authorization") if headers else None
        # )
        self._client = Client(
            transport=StreamableHttpTransport(
                url=endpoint_url,
                headers=headers,
            )
        )

    def is_connected(self):
        return self._client.is_connected()

    def capabilities(self) -> ServerCapabilities:
        """Get the server capabilities.

        Returns:
            ServerCapabilities: The server's capabilities object
        """
        return self._client.initialize_result.capabilities

    def prompt_enabled(self) -> bool:
        """Check if prompts are enabled on the server.

        Returns:
            bool: True if prompts are enabled, False otherwise
        """
        return self.capabilities().prompts is not None

    def resource_enabled(self) -> bool:
        """Check if resources are enabled on the server.

        Returns:
            bool: True if resources are enabled, False otherwise
        """
        return self.capabilities().resources is not None

    def experimental_enabled(self) -> bool:
        """Check if experimental features are enabled on the server.

        Returns:
            bool: True if experimental features are enabled, False otherwise
        """
        return self.capabilities().experimental is not None

    def logging_enabled(self) -> bool:
        """Check if logging is enabled on the server.

        Returns:
            bool: True if logging is enabled, False otherwise
        """
        return self.capabilities().logging is not None

    def tools_enabled(self) -> bool:
        """Check if tools are enabled on the server.

        Returns:
            bool: True if tools are enabled, False otherwise
        """
        return self.capabilities().tools is not None

    async def __aenter__(self):
        """Context manager entry."""
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools available from the MCP server.

        Returns:
            List[Dict[str, Any]]: List of tools with their metadata
        """
        return await self._client.list_tools()

    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List all prompts available from the MCP server.

        Returns:
            List[Dict[str, Any]]: List of prompts with their metadata
        """
        return await self._client.list_prompts()

    async def list_resources(self) -> List[Dict[str, Any]]:
        """List all resources available from the MCP server.

        Returns:
            List[Dict[str, Any]]: List of resources with their metadata
        """
        return await self._client.list_resources()
