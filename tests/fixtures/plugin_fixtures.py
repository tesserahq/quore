import pytest
from app.services.plugin_registry import PluginRegistryService
from app.schemas.plugin import PluginCreate


@pytest.fixture
def sample_plugin_data():
    return {
        "name": "Test Plugin",
        "description": "A test plugin",
        "version": "1.0.0",
        "author": "Test Author",
        "metadata_": {"type": "test"},
        "repository_url": "https://github.com/test/plugin",
    }


@pytest.fixture
def setup_plugin(db, sample_plugin_data, setup_workspace):
    workspace = setup_workspace
    return PluginRegistryService(db).register_plugin(
        PluginCreate(workspace_id=workspace.id, **sample_plugin_data)
    )
