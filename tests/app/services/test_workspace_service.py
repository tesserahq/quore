import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.services.workspace_service import WorkspaceService


@pytest.fixture
def sample_workspace_data():
    return {"name": "Test Workspace", "description": "A test workspace"}


def test_create_workspace(db: Session, setup_user, sample_workspace_data):
    # Create workspace
    user = setup_user
    sample_workspace_data = {**sample_workspace_data, "created_by_id": user.id}
    workspace_create = WorkspaceCreate(**sample_workspace_data)
    workspace = WorkspaceService(db).create_workspace(workspace_create)

    # Assertions
    assert workspace.id is not None
    assert workspace.name == sample_workspace_data["name"]
    assert workspace.description == sample_workspace_data["description"]
    assert workspace.created_by_id == sample_workspace_data["created_by_id"]
    assert workspace.created_at is not None
    assert workspace.updated_at is not None


def test_get_workspace(db: Session, setup_workspace):
    workspace = setup_workspace

    # Get workspace
    retrieved_workspace = WorkspaceService(db).get_workspace(workspace.id)

    # Assertions
    assert retrieved_workspace is not None
    assert retrieved_workspace.id == workspace.id
    assert retrieved_workspace.name == workspace.name


def test_get_workspace_not_found(db: Session):
    # Try to get non-existent workspace
    retrieved_workspace = WorkspaceService(db).get_workspace(uuid4())

    # Assertion
    assert retrieved_workspace is None


def test_get_workspaces(db: Session, setup_workspace):
    workspace = setup_workspace

    # Get all workspaces
    workspaces = WorkspaceService(db).get_workspaces()

    # Assertions
    assert len(workspaces) >= 1
    assert any(w.id == workspace.id for w in workspaces)


def test_update_workspace(db: Session, setup_workspace):
    workspace = setup_workspace

    # Update data
    update_data = {"name": "Updated Workspace", "description": "Updated description"}
    workspace_update = WorkspaceUpdate(**update_data)

    # Update workspace
    updated_workspace = WorkspaceService(db).update_workspace(
        workspace.id, workspace_update
    )

    # Assertions
    assert updated_workspace is not None
    assert updated_workspace.id == workspace.id
    assert updated_workspace.name == update_data["name"]
    assert updated_workspace.description == update_data["description"]


def test_update_workspace_not_found(db: Session):
    # Try to update non-existent workspace
    update_data = {"name": "Updated Workspace"}
    workspace_update = WorkspaceUpdate(**update_data)

    # Update workspace
    updated_workspace = WorkspaceService(db).update_workspace(uuid4(), workspace_update)

    # Assertion
    assert updated_workspace is None


def test_delete_workspace(db: Session, setup_workspace):
    workspace = setup_workspace

    # Delete workspace
    workspace_service = WorkspaceService(db)
    success = workspace_service.delete_workspace(workspace.id)

    # Assertions
    assert success is True
    deleted_workspace = workspace_service.get_workspace(workspace.id)
    assert deleted_workspace is None


def test_delete_workspace_not_found(db: Session):
    # Try to delete non-existent workspace
    success = WorkspaceService(db).delete_workspace(uuid4())

    # Assertion
    assert success is False


def test_search_workspaces_with_filters(db: Session, setup_workspace):
    workspace = setup_workspace

    # Search using ilike filter
    filters = {"name": {"operator": "ilike", "value": f"%{workspace.name}%"}}
    results = WorkspaceService(db).search(filters)

    assert isinstance(results, list)
    assert any(result.id == workspace.id for result in results)

    # Search using exact match
    filters = {"name": workspace.name}
    results = WorkspaceService(db).search(filters)

    assert len(results) == 1
    assert results[0].id == workspace.id

    # Search with no match
    filters = {"name": {"operator": "==", "value": "Nonexistent Name"}}
    results = WorkspaceService(db).search(filters)

    assert len(results) == 0


def test_create_workspace_with_identifier(db: Session, setup_user):
    """Test creating a workspace with an identifier field."""
    user = setup_user

    # Create workspace data with identifier
    workspace_data = {
        "name": "Test Workspace with Identifier",
        "description": "A test workspace with identifier",
        "identifier": "test-workspace-123",
        "created_by_id": user.id,
    }

    workspace_create = WorkspaceCreate(**workspace_data)
    workspace = WorkspaceService(db).create_workspace(workspace_create)

    # Assertions
    assert workspace.id is not None
    assert workspace.name == workspace_data["name"]
    assert workspace.description == workspace_data["description"]
    assert workspace.identifier == workspace_data["identifier"]
    assert workspace.created_by_id == workspace_data["created_by_id"]
    assert workspace.created_at is not None
    assert workspace.updated_at is not None


def test_create_workspace_with_duplicate_identifier(db: Session, setup_user):
    """Test that creating a workspace with a duplicate identifier fails."""
    user = setup_user

    # Create first workspace with identifier
    workspace_data_1 = {
        "name": "First Workspace",
        "description": "First workspace with identifier",
        "identifier": "duplicate-identifier",
        "created_by_id": user.id,
    }

    workspace_create_1 = WorkspaceCreate(**workspace_data_1)
    workspace_1 = WorkspaceService(db).create_workspace(workspace_create_1)

    # Try to create second workspace with same identifier
    workspace_data_2 = {
        "name": "Second Workspace",
        "description": "Second workspace with same identifier",
        "identifier": "duplicate-identifier",
        "created_by_id": user.id,
    }

    workspace_create_2 = WorkspaceCreate(**workspace_data_2)

    # This should raise an integrity error due to unique constraint
    with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
        WorkspaceService(db).create_workspace(workspace_create_2)


def test_update_workspace_with_identifier(db: Session, setup_workspace):
    """Test updating a workspace with an identifier field."""
    workspace = setup_workspace

    # Update data including identifier
    update_data = {
        "name": "Updated Workspace with Identifier",
        "description": "Updated description with identifier",
        "identifier": "updated-workspace-456",
    }
    workspace_update = WorkspaceUpdate(**update_data)

    # Update workspace
    updated_workspace = WorkspaceService(db).update_workspace(
        workspace.id, workspace_update
    )

    # Assertions
    assert updated_workspace is not None
    assert updated_workspace.id == workspace.id
    assert updated_workspace.name == update_data["name"]
    assert updated_workspace.description == update_data["description"]
    assert updated_workspace.identifier == update_data["identifier"]


def test_search_workspaces_by_identifier(db: Session, setup_user):
    """Test searching workspaces by identifier field."""
    user = setup_user

    # Create workspace with identifier
    workspace_data = {
        "name": "Searchable Workspace",
        "description": "A workspace for testing search",
        "identifier": "searchable-workspace",
        "created_by_id": user.id,
    }

    workspace_create = WorkspaceCreate(**workspace_data)
    workspace = WorkspaceService(db).create_workspace(workspace_create)

    # Search by exact identifier match
    filters = {"identifier": "searchable-workspace"}
    results = WorkspaceService(db).search(filters)

    assert len(results) == 1
    assert results[0].id == workspace.id
    assert results[0].identifier == workspace_data["identifier"]

    # Search by partial identifier match
    filters = {"identifier": {"operator": "ilike", "value": "%searchable%"}}
    results = WorkspaceService(db).search(filters)

    assert len(results) == 1
    assert results[0].id == workspace.id


def test_get_workspace_stats_empty_workspace(db: Session, setup_workspace):
    """Test get_workspace_stats with an empty workspace."""
    workspace = setup_workspace

    stats = WorkspaceService(db).get_workspace_stats(workspace.id)

    assert stats is not None
    assert stats.project_stats.total_projects == 0
    assert stats.project_stats.recent_projects == []
    assert stats.prompt_stats.total_prompts == 0
    assert stats.prompt_stats.recent_prompts == []
    assert stats.plugin_stats.total_enabled == 0
    assert stats.plugin_stats.total_disabled == 0
    assert stats.credential_stats.total_credentials == 0
    assert stats.credential_stats.recent_credentials == []


def test_get_workspace_stats_with_projects(db: Session, setup_workspace, setup_project):
    """Test get_workspace_stats with projects."""
    workspace = setup_workspace
    project = setup_project

    stats = WorkspaceService(db).get_workspace_stats(workspace.id)

    assert stats is not None
    assert stats.project_stats.total_projects == 1
    assert len(stats.project_stats.recent_projects) == 1
    assert stats.project_stats.recent_projects[0].id == project.id
    assert stats.project_stats.recent_projects[0].name == project.name
    assert stats.project_stats.recent_projects[0].description == project.description


def test_get_workspace_stats_with_prompts(db: Session, setup_workspace, setup_prompt):
    """Test get_workspace_stats with prompts."""
    workspace = setup_workspace
    prompt = setup_prompt

    stats = WorkspaceService(db).get_workspace_stats(workspace.id)

    assert stats is not None
    assert stats.prompt_stats.total_prompts == 1
    assert len(stats.prompt_stats.recent_prompts) == 1
    assert stats.prompt_stats.recent_prompts[0].id == prompt.id
    assert stats.prompt_stats.recent_prompts[0].name == prompt.name
    assert stats.prompt_stats.recent_prompts[0].type == prompt.type


def test_get_workspace_stats_with_plugins(db: Session, setup_workspace, setup_plugin):
    """Test get_workspace_stats with plugins."""
    workspace = setup_workspace
    plugin = setup_plugin

    stats = WorkspaceService(db).get_workspace_stats(workspace.id)

    assert stats is not None
    # Plugin should be counted as disabled (INITIALIZING state)
    assert stats.plugin_stats.total_enabled == 0
    assert stats.plugin_stats.total_disabled == 1


def test_get_workspace_stats_with_credentials(
    db: Session, setup_workspace, setup_credential
):
    """Test get_workspace_stats with credentials."""
    workspace = setup_workspace
    credential = setup_credential

    stats = WorkspaceService(db).get_workspace_stats(workspace.id)

    assert stats is not None
    assert stats.credential_stats.total_credentials == 1
    assert len(stats.credential_stats.recent_credentials) == 1
    assert stats.credential_stats.recent_credentials[0].id == credential.id
    assert stats.credential_stats.recent_credentials[0].name == credential.name
    assert stats.credential_stats.recent_credentials[0].type == credential.type


def test_get_workspace_stats_comprehensive(
    db: Session,
    setup_workspace,
    setup_project,
    setup_prompt,
    setup_plugin,
    setup_credential,
):
    """Test get_workspace_stats with all types of data."""
    workspace = setup_workspace
    project = setup_project
    prompt = setup_prompt
    plugin = setup_plugin
    credential = setup_credential

    stats = WorkspaceService(db).get_workspace_stats(workspace.id)

    assert stats is not None

    # Check projects
    assert stats.project_stats.total_projects == 1
    assert len(stats.project_stats.recent_projects) == 1
    assert stats.project_stats.recent_projects[0].id == project.id

    # Check prompts
    assert stats.prompt_stats.total_prompts == 1
    assert len(stats.prompt_stats.recent_prompts) == 1
    assert stats.prompt_stats.recent_prompts[0].id == prompt.id

    # Check plugins
    assert stats.plugin_stats.total_enabled == 0
    assert stats.plugin_stats.total_disabled == 1

    # Check credentials
    assert stats.credential_stats.total_credentials == 1
    assert len(stats.credential_stats.recent_credentials) == 1
    assert stats.credential_stats.recent_credentials[0].id == credential.id


def test_get_workspace_stats_multiple_items(db: Session, setup_workspace, faker):
    """Test get_workspace_stats with multiple items."""
    workspace = setup_workspace

    # Create multiple projects
    from app.models.project import Project
    from app.constants.providers import MOCK_PROVIDER

    projects = []
    for i in range(3):
        project = Project(
            name=f"Project {i}",
            description=f"Description {i}",
            workspace_id=workspace.id,
            llm_provider=MOCK_PROVIDER,
            embed_model="mock",
            embed_dim=1536,
            llm="mock",
        )
        db.add(project)
        projects.append(project)

    # Create multiple prompts
    from app.models.prompt import Prompt

    prompts = []
    for i in range(3):
        prompt = Prompt(
            name=f"Prompt {i}",
            prompt_id=faker.uuid4(),
            type=f"type_{i}",
            prompt=f"Prompt content {i}",
            workspace_id=workspace.id,
            created_by_id=workspace.created_by_id,
        )
        db.add(prompt)
        prompts.append(prompt)

    # Create multiple credentials
    from app.models.credential import Credential
    from app.core.credentials import encrypt_credential_fields

    credentials = []
    for i in range(3):
        # Encrypt the credential fields
        fields_data = {"field": f"value_{i}"}
        encrypted_data = encrypt_credential_fields(fields_data)

        credential = Credential(
            name=f"Credential {i}",
            type=f"type_{i}",
            encrypted_data=encrypted_data,
            workspace_id=workspace.id,
            created_by_id=workspace.created_by_id,
        )
        db.add(credential)
        credentials.append(credential)

    # Create multiple plugins
    from app.models.plugin import Plugin
    from app.constants.plugin_states import PluginState

    plugins = []
    for i in range(3):
        plugin = Plugin(
            name=f"Plugin {i}",
            description=f"Description {i}",
            version="1.0.0",
            state=PluginState.RUNNING if i % 2 == 0 else PluginState.STOPPED,
            endpoint_url=f"http://localhost:{8000 + i}",
            workspace_id=workspace.id,
        )
        db.add(plugin)
        plugins.append(plugin)

    db.commit()

    stats = WorkspaceService(db).get_workspace_stats(workspace.id)

    assert stats is not None

    # Check counts
    assert stats.project_stats.total_projects == 3
    assert stats.prompt_stats.total_prompts == 3
    assert stats.plugin_stats.total_enabled == 2  # 2 RUNNING plugins
    assert stats.plugin_stats.total_disabled == 1  # 1 STOPPED plugin
    assert stats.credential_stats.total_credentials == 3

    # Check recent items (should be limited to 5 most recent)
    assert len(stats.project_stats.recent_projects) == 3
    assert len(stats.prompt_stats.recent_prompts) == 3
    assert len(stats.credential_stats.recent_credentials) == 3


def test_get_workspace_stats_nonexistent_workspace(db: Session):
    """Test get_workspace_stats with nonexistent workspace."""
    import uuid

    nonexistent_id = uuid.uuid4()
    stats = WorkspaceService(db).get_workspace_stats(nonexistent_id)

    assert stats is None


def test_get_workspace_stats_plugin_states(db: Session, setup_workspace):
    """Test get_workspace_stats with different plugin states."""
    workspace = setup_workspace

    # Create plugins with different states
    from app.models.plugin import Plugin
    from app.constants.plugin_states import PluginState

    # Enabled states: RUNNING, IDLE, STARTING
    enabled_plugins = []
    for state in [PluginState.RUNNING, PluginState.IDLE, PluginState.STARTING]:
        plugin = Plugin(
            name=f"Enabled Plugin {state}",
            description=f"Description {state}",
            version="1.0.0",
            state=state,
            endpoint_url="http://localhost:8000",
            workspace_id=workspace.id,
        )
        db.add(plugin)
        enabled_plugins.append(plugin)

    # Disabled states: STOPPED, ERROR, REGISTERED, INITIALIZING
    disabled_plugins = []
    for state in [
        PluginState.STOPPED,
        PluginState.ERROR,
        PluginState.REGISTERED,
        PluginState.INITIALIZING,
    ]:
        plugin = Plugin(
            name=f"Disabled Plugin {state}",
            description=f"Description {state}",
            version="1.0.0",
            state=state,
            endpoint_url="http://localhost:8000",
            workspace_id=workspace.id,
        )
        db.add(plugin)
        disabled_plugins.append(plugin)

    db.commit()

    stats = WorkspaceService(db).get_workspace_stats(workspace.id)

    assert stats is not None
    assert stats.plugin_stats.total_enabled == 3  # RUNNING, IDLE, STARTING
    assert (
        stats.plugin_stats.total_disabled == 4
    )  # STOPPED, ERROR, REGISTERED, INITIALIZING


def test_get_workspace_stats_recent_items_limit(db: Session, setup_workspace, faker):
    """Test get_workspace_stats ensures recent items are limited to 5."""
    workspace = setup_workspace

    # Create more than 5 projects
    from app.models.project import Project
    from app.constants.providers import MOCK_PROVIDER

    for i in range(7):
        project = Project(
            name=f"Project {i}",
            description=f"Description {i}",
            workspace_id=workspace.id,
            llm_provider=MOCK_PROVIDER,
            embed_model="mock",
            embed_dim=1536,
            llm="mock",
        )
        db.add(project)

    # Create more than 5 prompts
    from app.models.prompt import Prompt

    for i in range(7):
        prompt = Prompt(
            name=f"Prompt {i}",
            prompt_id=faker.uuid4(),
            type=f"type_{i}",
            prompt=f"Prompt content {i}",
            workspace_id=workspace.id,
            created_by_id=workspace.created_by_id,
        )
        db.add(prompt)

    # Create more than 5 credentials
    from app.models.credential import Credential
    from app.core.credentials import encrypt_credential_fields

    for i in range(7):
        fields_data = {"field": f"value_{i}"}
        encrypted_data = encrypt_credential_fields(fields_data)

        credential = Credential(
            name=f"Credential {i}",
            type=f"type_{i}",
            encrypted_data=encrypted_data,
            workspace_id=workspace.id,
            created_by_id=workspace.created_by_id,
        )
        db.add(credential)

    db.commit()

    stats = WorkspaceService(db).get_workspace_stats(workspace.id)

    assert stats is not None
    assert stats.project_stats.total_projects == 7
    assert len(stats.project_stats.recent_projects) == 5  # Limited to 5
    assert stats.prompt_stats.total_prompts == 7
    assert len(stats.prompt_stats.recent_prompts) == 5  # Limited to 5
    assert stats.credential_stats.total_credentials == 7
    assert len(stats.credential_stats.recent_credentials) == 5  # Limited to 5


def test_create_workspace_with_system_prompt(db: Session, setup_user, faker):
    """Ensure system_prompt is persisted on create and can be updated."""
    user = setup_user

    workspace_data = {
        "name": faker.company(),
        "description": faker.text(50),
        "created_by_id": user.id,
        "system_prompt": "You are a helpful workspace assistant.",
    }

    workspace_create = WorkspaceCreate(**workspace_data)
    workspace = WorkspaceService(db).create_workspace(workspace_create)

    assert workspace.system_prompt == "You are a helpful workspace assistant."

    # Update the system_prompt
    workspace_update = WorkspaceUpdate(system_prompt="New workspace system prompt")
    updated_workspace = WorkspaceService(db).update_workspace(
        workspace.id, workspace_update
    )

    assert updated_workspace is not None
    assert updated_workspace.system_prompt == "New workspace system prompt"
