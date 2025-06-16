from typing import List, Dict, Any, Optional
from fastmcp import Client as FastMCPClient


class MCPClient:
    """A wrapper around the FastMCP client to provide a clean interface and allow for future implementation changes."""

    def __init__(self, endpoint_url: str, headers: Optional[Dict[str, str]] = None):
        """Initialize the MCP client with the given endpoint URL.

        Args:
            endpoint_url (str): The URL of the MCP server endpoint
            headers (Optional[Dict[str, str]]): Optional headers to pass to the client
        """
        self.endpoint_url = endpoint_url
        self._client: FastMCPClient = FastMCPClient(
            endpoint_url, auth=headers.get("Authorization") if headers else None
        )

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
