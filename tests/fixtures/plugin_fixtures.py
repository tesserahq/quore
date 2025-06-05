import pytest
from app.services.plugin_registry import PluginRegistryService
from app.schemas.plugin import PluginCreate
from app.constants.plugin_states import PluginState


@pytest.fixture
def sample_plugin_data():
    return {
        "name": "Test Plugin",
        "description": "A test plugin",
        "version": "1.0.0",
        "author": "Test Author",
        "metadata_": {"type": "test"},
        "credential_id": None,  # No credential by default
    }


@pytest.fixture
def setup_plugin(db, setup_workspace):
    """Create a test plugin."""
    plugin_data = PluginCreate(
        name="Test Plugin",
        description="A test plugin",
        version="1.0.0",
        state=PluginState.REGISTERED,
        endpoint_url="http://localhost:8000",
        plugin_metadata={"type": "test"},
        credential_id=None,  # No credential by default
        workspace_id=setup_workspace.id,
    )
    plugin = PluginRegistryService(db).create_plugin(plugin_data)
    return plugin
