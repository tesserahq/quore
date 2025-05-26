import pytest
from uuid import UUID, uuid4
from sqlalchemy.exc import IntegrityError
from app.services.plugin_registry import PluginRegistryService
from app.schemas.plugin import PluginCreate, PluginToolCreate
from app.models.plugin import Plugin
from app.models.plugin_tool import PluginTool
from app.models.project_plugin import ProjectPlugin
from app.models.project_plugin_tool import ProjectPluginTool
from tests.fixtures.workspace_fixtures import setup_workspace
from tests.fixtures.project_fixtures import setup_project
from unittest.mock import patch, MagicMock
import subprocess


# Global fixture to mock PluginManager.clone_repository for all tests
@pytest.fixture(autouse=True)
def mock_plugin_manager_clone_repository():
    with patch(
        "app.core.plugin_manager.manager.PluginManager.clone_repository"
    ) as mock_clone:
        mock_clone.return_value = None  # Simulate success
        yield mock_clone


@pytest.fixture
def plugin_registry_service(db):
    return PluginRegistryService(db)


@pytest.fixture
def sample_plugin_data(setup_workspace):
    return PluginCreate(
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


@pytest.fixture
def sample_tool_data():
    return PluginToolCreate(
        name="test_tool",
        description="A test tool",
        is_active=True,
        input_schema={"type": "object", "properties": {"param": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"result": {"type": "string"}}},
        tool_metadata={"category": "test"},
    )


@pytest.fixture
def created_plugin(plugin_registry_service, sample_plugin_data):
    return plugin_registry_service.register_plugin(sample_plugin_data)


@pytest.fixture
def created_tool(plugin_registry_service, created_plugin, sample_tool_data):
    return plugin_registry_service.register_tool(created_plugin.id, sample_tool_data)


class TestPluginRegistryService:
    def test_register_plugin(self, plugin_registry_service, sample_plugin_data):
        """Test registering a plugin and cloning its repository."""
        with patch(
            "app.core.plugin_manager.manager.PluginManager.clone_repository"
        ) as mock_clone:
            plugin = plugin_registry_service.register_plugin(sample_plugin_data)

            assert plugin is not None
            assert plugin.name == sample_plugin_data.name
            assert plugin.description == sample_plugin_data.description
            assert plugin.repository_url == sample_plugin_data.repository_url
            assert plugin.version == sample_plugin_data.version
            assert plugin.commit_hash == sample_plugin_data.commit_hash
            assert plugin.is_active == sample_plugin_data.is_active
            assert plugin.endpoint_url == sample_plugin_data.endpoint_url
            assert plugin.plugin_metadata == sample_plugin_data.plugin_metadata
            assert plugin.credential_id == sample_plugin_data.credential_id
            assert plugin.workspace_id == sample_plugin_data.workspace_id

            # Verify that clone_repository was called
            mock_clone.assert_called_once()

    def test_register_plugin_clone_failure(
        self, plugin_registry_service, sample_plugin_data
    ):
        """Test that plugin registration is rolled back if repository cloning fails."""
        with patch(
            "app.core.plugin_manager.manager.PluginManager.clone_repository"
        ) as mock_clone:
            mock_clone.side_effect = RuntimeError("Failed to clone repository")

            # Verify that the error is propagated
            with pytest.raises(RuntimeError) as exc_info:
                plugin_registry_service.register_plugin(sample_plugin_data)
            assert "Failed to clone plugin repository" in str(exc_info.value)

            # Verify that the plugin was not created
            plugins = plugin_registry_service.get_workspace_plugins(
                sample_plugin_data.workspace_id
            )
            assert len(plugins) == 0

    def test_get_plugin(self, plugin_registry_service, created_plugin):
        retrieved_plugin = plugin_registry_service.get_plugin(created_plugin.id)

        assert retrieved_plugin is not None
        assert retrieved_plugin.id == created_plugin.id
        assert retrieved_plugin.name == created_plugin.name

    def test_update_plugin(self, plugin_registry_service, created_plugin):
        update_data = PluginCreate(
            name="Updated Plugin",
            description="Updated description",
            version="2.0.0",
            repository_url=created_plugin.repository_url,
            commit_hash=created_plugin.commit_hash,
            is_active=created_plugin.is_active,
            endpoint_url=created_plugin.endpoint_url,
            plugin_metadata=created_plugin.plugin_metadata,
            credential_id=created_plugin.credential_id,
            workspace_id=created_plugin.workspace_id,
        )

        updated_plugin = plugin_registry_service.update_plugin(
            created_plugin.id, update_data
        )

        assert updated_plugin is not None
        assert updated_plugin.name == update_data.name
        assert updated_plugin.description == update_data.description
        assert updated_plugin.version == update_data.version
        assert updated_plugin.repository_url == created_plugin.repository_url
        assert updated_plugin.commit_hash == created_plugin.commit_hash
        assert updated_plugin.is_active == created_plugin.is_active
        assert updated_plugin.endpoint_url == created_plugin.endpoint_url
        assert updated_plugin.plugin_metadata == created_plugin.plugin_metadata
        assert updated_plugin.credential_id == created_plugin.credential_id
        assert updated_plugin.workspace_id == created_plugin.workspace_id

    def test_delete_plugin(self, plugin_registry_service, created_plugin):
        result = plugin_registry_service.delete_plugin(created_plugin.id)

        assert result is True
        assert plugin_registry_service.get_plugin(created_plugin.id) is None

    def test_register_tool(
        self, plugin_registry_service, created_plugin, sample_tool_data
    ):
        tool = plugin_registry_service.register_tool(
            created_plugin.id, sample_tool_data
        )

        assert tool is not None
        assert tool.name == sample_tool_data.name
        assert tool.description == sample_tool_data.description
        assert tool.is_active == sample_tool_data.is_active
        assert tool.input_schema == sample_tool_data.input_schema
        assert tool.output_schema == sample_tool_data.output_schema
        assert tool.tool_metadata == sample_tool_data.tool_metadata

    def test_get_plugin_tools(
        self, plugin_registry_service, created_plugin, created_tool
    ):
        tools = plugin_registry_service.get_plugin_tools(created_plugin.id)

        assert len(tools) == 1
        assert tools[0].id == created_tool.id
        assert tools[0].name == created_tool.name

    def test_enable_plugin_in_project(
        self, plugin_registry_service, created_plugin, setup_project
    ):
        project = setup_project
        config = {"project_specific": "config"}

        project_plugin = plugin_registry_service.enable_plugin_in_project(
            project.id, created_plugin.id, config
        )

        assert project_plugin is not None
        assert project_plugin.project_id == project.id
        assert project_plugin.plugin_id == created_plugin.id
        assert project_plugin.is_enabled is True
        assert project_plugin.config == config

    def test_enable_plugin_in_project_twice(
        self, plugin_registry_service, created_plugin, setup_project
    ):
        project = setup_project
        initial_config = {"initial": "config"}
        updated_config = {"updated": "config"}

        # First enable
        project_plugin = plugin_registry_service.enable_plugin_in_project(
            project.id, created_plugin.id, initial_config
        )

        # Second enable with new config
        updated_project_plugin = plugin_registry_service.enable_plugin_in_project(
            project.id, created_plugin.id, updated_config
        )

        assert updated_project_plugin is not None
        assert updated_project_plugin.id == project_plugin.id  # Same record
        assert updated_project_plugin.is_enabled is True
        assert updated_project_plugin.config == updated_config

    def test_disable_plugin_in_project(
        self, plugin_registry_service, created_plugin, setup_project
    ):
        project = setup_project
        project_plugin = plugin_registry_service.enable_plugin_in_project(
            project.id, created_plugin.id
        )

        result = plugin_registry_service.disable_plugin_in_project(
            project.id, created_plugin.id
        )

        assert result is True
        project_plugin = (
            plugin_registry_service.db.query(ProjectPlugin)
            .filter(
                ProjectPlugin.project_id == project.id,
                ProjectPlugin.plugin_id == created_plugin.id,
            )
            .first()
        )
        assert project_plugin.is_enabled is False

    def test_get_enabled_tools_for_project(
        self,
        plugin_registry_service,
        created_plugin,
        created_tool,
        setup_workspace,
        setup_project,
    ):
        workspace = setup_workspace
        project = setup_project

        # Enable plugin in project
        project_plugin = plugin_registry_service.enable_plugin_in_project(
            project.id, created_plugin.id
        )

        # Get enabled tools for project
        enabled_tools = plugin_registry_service.get_enabled_tools_for_project(
            project.id
        )

        assert len(enabled_tools) == 1
        assert enabled_tools[0].id == created_tool.id

    def test_get_enabled_tools_for_workspace(
        self, plugin_registry_service, setup_workspace, created_plugin, created_tool
    ):
        workspace = setup_workspace

        # Get enabled tools for workspace
        enabled_tools = plugin_registry_service.get_enabled_tools_for_workspace(
            workspace.id
        )

        assert len(enabled_tools) == 1
        assert enabled_tools[0].id == created_tool.id

    def test_update_tool_config(
        self, plugin_registry_service, created_plugin, created_tool, setup_project
    ):
        project = setup_project

        # Enable plugin in project
        project_plugin = plugin_registry_service.enable_plugin_in_project(
            project.id, created_plugin.id
        )

        # Enable tool in project
        plugin_registry_service.enable_tool_in_project(project.id, created_tool.id)

        # Update project tool config
        new_config = {"updated": "config"}
        result = plugin_registry_service.update_tool_config(
            created_tool.id, project_id=project.id, config=new_config
        )

        assert result is True
        project_tool = (
            plugin_registry_service.db.query(ProjectPluginTool)
            .filter(
                ProjectPluginTool.project_plugin_id == project_plugin.id,
                ProjectPluginTool.tool_id == created_tool.id,
            )
            .first()
        )
        assert project_tool.config == new_config
