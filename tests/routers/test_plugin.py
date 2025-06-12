import pytest
from app.services.plugin import PluginService
from app.models.project_plugin import ProjectPlugin
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.constants.plugin_states import PluginState

from app.models.plugin import Plugin

# Sample tools response
SAMPLE_TOOLS_RESPONSE = [
    {
        "name": "list_accounts",
        "description": "List all accounts",
        "inputSchema": {"properties": {}, "type": "object"},
        "annotations": None,
    },
    {
        "name": "create_account",
        "description": "Create a new account",
        "inputSchema": {
            "properties": {
                "name": {"title": "Name", "type": "string"},
                "description": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Description",
                },
            },
            "required": ["name"],
            "type": "object",
        },
        "annotations": None,
    },
]


@pytest.fixture
def mock_plugin(db: Session):
    """Create a test plugin in the database."""
    plugin = Plugin(
        name="Test Plugin",
        description="A test plugin",
        endpoint_url="http://test-plugin.example.com",
    )
    db.add(plugin)
    db.commit()
    db.refresh(plugin)
    return plugin


@pytest.fixture
def mock_mcp_client():
    """Mock the MCPClient for testing."""
    with patch("app.routers.plugin.MCPClient") as mock_client:
        # Create a mock instance
        mock_instance = AsyncMock()
        # Set up the context manager
        mock_client.return_value.__aenter__.return_value = mock_instance
        # Set up the list_tools method
        mock_instance.list_tools.return_value = SAMPLE_TOOLS_RESPONSE
        yield mock_client


def test_list_workspace_plugins(client, db, setup_workspace, setup_plugin):
    """Test listing plugins in a workspace."""
    workspace = setup_workspace
    plugin = setup_plugin
    response = client.get(f"/workspaces/{workspace.id}/plugins")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == str(plugin.id)
    assert data["data"][0]["name"] == "Test Plugin"


def test_create_workspace_plugin(client, db, setup_workspace):
    """Test creating a workspace plugin."""
    workspace = setup_workspace
    plugin_data = {
        "name": "New Plugin",
        "description": "A new plugin",
        "version": "1.0.0",
        "author": "Test Author",
        "plugin_metadata": {"type": "test"},
        "endpoint_url": "http://test-plugin.example.com",
    }

    response = client.post(f"/workspaces/{workspace.id}/plugins", json=plugin_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Plugin"
    assert data["workspace_id"] == str(workspace.id)

    # Verify plugin was created in database
    plugin = PluginService(db).get_plugin(data["id"])
    assert plugin is not None
    assert plugin.name == "New Plugin"
    assert plugin.workspace_id == workspace.id


def test_list_project_plugins(client, db, setup_project, setup_plugin):
    """Test listing plugins in a project."""
    project = setup_project
    plugin = setup_plugin
    # Enable the plugin in the project
    PluginService(db).enable_plugin_in_project(project.id, plugin.id)

    response = client.get(f"/projects/{project.id}/plugins")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == str(setup_plugin.id)
    assert data["data"][0]["name"] == "Test Plugin"


def test_enable_project_plugin(
    client, db, setup_workspace, setup_project, setup_plugin
):
    """Test enabling a plugin in a project."""
    workspace = setup_workspace
    project = setup_project
    plugin = setup_plugin
    config = {"setting": "value"}
    response = client.post(
        f"/projects/{project.id}/plugins/{plugin.id}",
        json={"config": config},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(setup_plugin.id)
    assert data["name"] == setup_plugin.name
    assert data["workspace_id"] == str(workspace.id)

    # Verify plugin was enabled in project
    project_plugin = (
        db.query(ProjectPlugin)
        .filter(
            ProjectPlugin.project_id == setup_project.id,
            ProjectPlugin.plugin_id == setup_plugin.id,
        )
        .first()
    )
    assert project_plugin is not None
    assert project_plugin.is_enabled is True
    assert project_plugin.config == {"config": config}


def test_inspect_tools_plugin_success(
    client: TestClient, setup_plugin: Plugin, mock_mcp_client
):
    """Test successful retrieval of plugin tools."""
    plugin = setup_plugin
    response = client.get(f"/plugins/{plugin.id}/inspect/tools")

    assert response.status_code == 200
    assert response.json() == SAMPLE_TOOLS_RESPONSE

    # Verify the mock was called correctly
    mock_mcp_client.assert_called_once_with(plugin.endpoint_url)
    mock_instance = mock_mcp_client.return_value.__aenter__.return_value
    mock_instance.list_tools.assert_called_once()


def test_list_plugin_states(client: TestClient):
    """Test retrieving the list of available plugin states."""
    response = client.get("/plugins/states")

    assert response.status_code == 200
    data = response.json()
    assert "states" in data
    assert isinstance(data["states"], list)

    # Convert response to a dict for easier comparison
    states_dict = {state["value"]: state["description"] for state in data["states"]}

    # Verify each state from the enum is present with correct description
    for state in PluginState:
        assert state.value in states_dict
        assert states_dict[state.value] == (state.__doc__ or state.value)

    # Verify no extra states were added
    assert len(states_dict) == len(PluginState)


def test_delete_plugin(client, db, setup_plugin):
    """Test deleting a plugin."""
    plugin = setup_plugin

    # Delete the plugin
    response = client.delete(f"/plugins/{plugin.id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Plugin deleted successfully"}

    # Verify plugin was deleted from database
    with pytest.raises(ValueError) as exc_info:
        PluginService(db).get_plugin(plugin.id)
    assert str(exc_info.value) == f"Plugin with ID {plugin.id} not found"
