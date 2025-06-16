import pytest
from unittest.mock import patch, AsyncMock
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.core.plugin_manager.manager import PluginManager
from app.constants.plugin_states import PluginState
from app.services.plugin import PluginService


class Tool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]
    annotations: Optional[Any] = None


class Resource(BaseModel):
    name: str
    description: str
    schema: Dict[str, Any]


class Prompt(BaseModel):
    name: str
    description: str
    template: str


# Sample responses for MCP client
SAMPLE_TOOLS = [
    Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={"type": "object", "properties": {}},
        annotations=None,
    )
]

SAMPLE_RESOURCES = [
    Resource(
        name="test_resource",
        description="A test resource",
        schema={"type": "object", "properties": {}},
    )
]

SAMPLE_PROMPTS = [
    Prompt(
        name="test_prompt",
        description="A test prompt",
        template="This is a test prompt",
    )
]


@pytest.fixture
def mock_mcp_client():
    """Mock the MCPClient for testing."""
    with patch("app.core.plugin_manager.manager.MCPClient") as mock_client:
        # Create a mock instance with async methods
        mock_instance = AsyncMock()
        mock_instance.list_tools = AsyncMock(return_value=SAMPLE_TOOLS)
        mock_instance.list_resources = AsyncMock(return_value=SAMPLE_RESOURCES)
        mock_instance.list_prompts = AsyncMock(return_value=SAMPLE_PROMPTS)

        # Set up the async context manager
        mock_client.return_value = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        mock_client.return_value.__aexit__ = AsyncMock()

        # Make the mock accept any arguments and return the same instance
        def create_mock(*args, **kwargs):
            print(f"MCPClient called with args: {args}, kwargs: {kwargs}")
            return mock_client.return_value

        mock_client.side_effect = create_mock

        yield mock_client


@pytest.mark.asyncio
class TestPluginManager:
    async def test_refresh_success(self, db, setup_plugin, mock_mcp_client):
        """Test successful plugin refresh."""
        print(f"Initial plugin state: {setup_plugin.state}")
        plugin_manager = PluginManager(db, setup_plugin.id)
        await plugin_manager.refresh()

        # Verify plugin was updated
        updated_plugin = PluginService(db).get_plugin(setup_plugin.id)
        print(f"Updated plugin state: {updated_plugin.state}")
        print(f"Updated plugin state description: {updated_plugin.state_description}")
        assert updated_plugin.state == PluginState.RUNNING
        assert [Tool(**tool) for tool in updated_plugin.tools] == SAMPLE_TOOLS
        assert [
            Resource(**resource) for resource in updated_plugin.resources
        ] == SAMPLE_RESOURCES
        assert [Prompt(**prompt) for prompt in updated_plugin.prompts] == SAMPLE_PROMPTS
