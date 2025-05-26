import pytest
from uuid import uuid4
from app.services.plugin_registry import PluginRegistryService
from app.schemas.plugin import PluginCreate, PluginToolCreate
from app.models.plugin import Plugin
from app.models.project_plugin import ProjectPlugin
from tests.fixtures.workspace_fixtures import setup_workspace
from tests.fixtures.project_fixtures import setup_project
from tests.fixtures.plugin_fixtures import sample_plugin_data, setup_plugin
from unittest.mock import patch


# Global fixture to mock PluginManager.clone_repository for all tests
@pytest.fixture(autouse=True)
def mock_plugin_manager_clone_repository():
    with patch(
        "app.core.plugin_manager.manager.PluginManager.clone_repository"
    ) as mock_clone:
        mock_clone.return_value = None  # Simulate success
        yield mock_clone


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
        "repository_url": "https://github.com/test/plugin",
    }

    response = client.post(f"/workspaces/{workspace.id}/plugins", json=plugin_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Plugin"
    assert data["workspace_id"] == str(workspace.id)

    # Verify plugin was created in database
    plugin = PluginRegistryService(db).get_plugin(data["id"])
    assert plugin is not None
    assert plugin.name == "New Plugin"
    assert plugin.workspace_id == workspace.id


def test_list_project_plugins(client, db, setup_project, setup_plugin):
    """Test listing plugins in a project."""
    project = setup_project
    plugin = setup_plugin
    # Enable the plugin in the project
    PluginRegistryService(db).enable_plugin_in_project(project.id, plugin.id)

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
