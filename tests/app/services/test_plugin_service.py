import pytest
from app.services.plugin_service import PluginService
from app.schemas.plugin import PluginCreate
from app.constants.plugin_states import PluginState


@pytest.fixture
def plugin_service(db):
    return PluginService(db)


@pytest.fixture
def sample_plugin_data(setup_workspace):
    return PluginCreate(
        name="Test Plugin",
        description="A test plugin",
        version="1.0.0",
        state=PluginState.REGISTERED,
        endpoint_url="http://localhost:8000",
        plugin_metadata={"type": "test"},
        credential_id=None,  # No credential by default
        workspace_id=setup_workspace.id,
    )


@pytest.fixture
def created_plugin(plugin_service, sample_plugin_data):
    return plugin_service.create_plugin(sample_plugin_data)


class TestPluginService:
    def test_create_plugin(self, plugin_service, sample_plugin_data):
        """Test registering a plugin."""

        plugin = plugin_service.create_plugin(sample_plugin_data)

        assert plugin is not None
        assert plugin.name == sample_plugin_data.name
        assert plugin.description == sample_plugin_data.description
        assert plugin.version == sample_plugin_data.version
        assert plugin.state == PluginState.INITIALIZING
        assert plugin.endpoint_url == sample_plugin_data.endpoint_url
        assert plugin.plugin_metadata == sample_plugin_data.plugin_metadata
        assert plugin.credential_id == sample_plugin_data.credential_id
        assert plugin.workspace_id == sample_plugin_data.workspace_id

    def test_get_plugin(self, plugin_service, created_plugin):
        retrieved_plugin = plugin_service.get_plugin(created_plugin.id)

        assert retrieved_plugin is not None
        assert retrieved_plugin.id == created_plugin.id
        assert retrieved_plugin.name == created_plugin.name

    def test_update_plugin(self, plugin_service, created_plugin):
        update_data = PluginCreate(
            name="Updated Plugin",
            description="Updated description",
            version="2.0.0",
            state=created_plugin.state,
            endpoint_url=created_plugin.endpoint_url,
            plugin_metadata=created_plugin.plugin_metadata,
            credential_id=created_plugin.credential_id,
            workspace_id=created_plugin.workspace_id,
        )

        updated_plugin = plugin_service.update_plugin(created_plugin.id, update_data)

        assert updated_plugin is not None
        assert updated_plugin.name == update_data.name
        assert updated_plugin.description == update_data.description
        assert updated_plugin.version == update_data.version
        assert updated_plugin.state == created_plugin.state
        assert updated_plugin.endpoint_url == created_plugin.endpoint_url
        assert updated_plugin.plugin_metadata == created_plugin.plugin_metadata
        assert updated_plugin.credential_id == created_plugin.credential_id
        assert updated_plugin.workspace_id == created_plugin.workspace_id

    def test_delete_plugin(self, plugin_service, created_plugin):
        result = plugin_service.delete_plugin(created_plugin.id)

        assert result is True
        with pytest.raises(ValueError) as exc_info:
            plugin_service.get_plugin(created_plugin.id)
        assert str(exc_info.value) == f"Plugin with ID {created_plugin.id} not found"
