import pytest
from app.services.plugin_registry import PluginRegistryService
from app.schemas.plugin import PluginCreate
from uuid import uuid4


@pytest.fixture
def sample_plugin_data():
    return {
        "name": "Test Plugin",
        "description": "A test plugin",
        "version": "1.0.0",
        "author": "Test Author",
        "metadata_": {"type": "test"},
        "repository_url": "https://github.com/test/plugin",
        "credential_id": None,  # No credential by default
    }


@pytest.fixture
def setup_plugin(db, setup_workspace):
    """Create a test plugin."""
    plugin_data = PluginCreate(
        name="Test Plugin",
        description="A test plugin",
        repository_url="https://github.com/test/plugin",
        version="1.0.0",
        commit_hash="abc123",
        is_active=True,
        endpoint_url="http://localhost:8000",
        plugin_metadata={"type": "test"},
        credential_id=None,  # No credential by default
        workspace_id=setup_workspace.id,
    )
    plugin = PluginRegistryService(db).register_plugin(plugin_data)
    return plugin
