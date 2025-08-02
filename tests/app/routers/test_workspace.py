def test_list_workspaces(client, setup_workspace, setup_different_workspace):
    """Test GET /workspaces endpoint."""
    workspace = setup_workspace
    _ = setup_different_workspace

    # Ensure the workspace is created
    response = client.get("/workspaces")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)

    # Make sure the response contains the correct workspace
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == str(workspace.id)
    assert data["data"][0]["name"] == workspace.name
    assert data["data"][0]["description"] == workspace.description
    assert data["data"][0]["created_by_id"] == str(workspace.created_by_id)


def test_get_workspace(client, setup_workspace):
    """Test GET /workspaces/{workspace_id} endpoint."""
    workspace = setup_workspace
    response = client.get(f"/workspaces/{workspace.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(workspace.id)
    assert response.json()["name"] == workspace.name
    assert response.json()["description"] == workspace.description
    assert response.json()["created_by_id"] == str(workspace.created_by_id)


def test_create_workspace(client, setup_user):
    """Test POST /workspaces endpoint."""

    user = setup_user

    response = client.post(
        "/workspaces",
        json={"name": "Test Workspace"},
    )
    assert response.status_code == 201
    workspace = response.json()
    assert workspace["name"] == "Test Workspace"
    assert workspace["created_by_id"] == str(user.id)

    # Verify that a membership was created for the workspace creator
    workspace_id = workspace["id"]
    membership_response = client.get(f"/workspaces/{workspace_id}/memberships")
    assert membership_response.status_code == 200

    memberships = membership_response.json()["data"]
    assert len(memberships) == 1

    membership = memberships[0]
    assert membership["user_id"] == str(user.id)
    assert membership["workspace_id"] == workspace_id
    assert membership["role"] == "owner"  # Should be owner role


def test_create_workspace_invalid_data(client, setup_user):
    """Test POST /workspaces endpoint with invalid data."""
    invalid_workspace_data = {
        "name": "",  # Empty name should be invalid
        "description": "A test workspace description",
    }

    response = client.post("/workspaces", json=invalid_workspace_data)
    assert response.status_code == 422  # Validation error


def test_create_workspace_missing_name(client, setup_user):
    """Test POST /workspaces endpoint with missing name field."""
    invalid_workspace_data = {
        "description": "A test workspace description",
        # Missing 'name' field
    }

    response = client.post("/workspaces", json=invalid_workspace_data)
    assert response.status_code == 422  # Validation error


def test_update_workspace_invalid_data(client, setup_workspace):
    """Test PUT /workspaces/{workspace_id} endpoint with invalid data."""
    workspace = setup_workspace
    invalid_update_data = {
        "name": "",  # Empty name should be invalid
        "description": "Updated description",
    }

    response = client.put(f"/workspaces/{workspace.id}", json=invalid_update_data)
    assert response.status_code == 422  # Validation error


def test_delete_workspace(client, setup_workspace):
    """Test DELETE /workspaces/{workspace_id} endpoint."""
    workspace = setup_workspace
    response = client.delete(f"/workspaces/{workspace.id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Workspace deleted successfully"}

    # Verify the workspace is deleted
    response = client.get(f"/workspaces/{workspace.id}")
    assert response.status_code == 404


def test_get_workspace_stats_empty_workspace(client, setup_workspace):
    """Test GET /workspaces/{workspace_id}/stats endpoint with empty workspace."""
    workspace = setup_workspace
    response = client.get(f"/workspaces/{workspace.id}/stats")
    assert response.status_code == 200

    data = response.json()
    assert data["project_stats"]["total_projects"] == 0
    assert data["project_stats"]["recent_projects"] == []
    assert data["prompt_stats"]["total_prompts"] == 0
    assert data["prompt_stats"]["recent_prompts"] == []
    assert data["plugin_stats"]["total_enabled"] == 0
    assert data["plugin_stats"]["total_disabled"] == 0
    assert data["credential_stats"]["total_credentials"] == 0
    assert data["credential_stats"]["recent_credentials"] == []


def test_get_workspace_stats_with_projects(client, setup_workspace, setup_project):
    """Test GET /workspaces/{workspace_id}/stats endpoint with projects."""
    workspace = setup_workspace
    project = setup_project

    response = client.get(f"/workspaces/{workspace.id}/stats")
    assert response.status_code == 200

    data = response.json()
    assert data["project_stats"]["total_projects"] == 1
    assert len(data["project_stats"]["recent_projects"]) == 1
    assert data["project_stats"]["recent_projects"][0]["id"] == str(project.id)
    assert data["project_stats"]["recent_projects"][0]["name"] == project.name
    assert (
        data["project_stats"]["recent_projects"][0]["description"]
        == project.description
    )


def test_get_workspace_stats_with_prompts(client, setup_workspace, setup_prompt):
    """Test GET /workspaces/{workspace_id}/stats endpoint with prompts."""
    workspace = setup_workspace
    prompt = setup_prompt

    response = client.get(f"/workspaces/{workspace.id}/stats")
    assert response.status_code == 200

    data = response.json()
    assert data["prompt_stats"]["total_prompts"] == 1
    assert len(data["prompt_stats"]["recent_prompts"]) == 1
    assert data["prompt_stats"]["recent_prompts"][0]["id"] == str(prompt.id)
    assert data["prompt_stats"]["recent_prompts"][0]["name"] == prompt.name
    assert data["prompt_stats"]["recent_prompts"][0]["type"] == prompt.type


def test_get_workspace_stats_with_plugins(client, setup_workspace, setup_plugin):
    """Test GET /workspaces/{workspace_id}/stats endpoint with plugins."""
    workspace = setup_workspace
    plugin = setup_plugin

    response = client.get(f"/workspaces/{workspace.id}/stats")
    assert response.status_code == 200

    data = response.json()
    # Plugin should be counted as disabled (INITIALIZING state)
    assert data["plugin_stats"]["total_enabled"] == 0
    assert data["plugin_stats"]["total_disabled"] == 1


def test_get_workspace_stats_with_credentials(
    client, setup_workspace, setup_credential
):
    """Test GET /workspaces/{workspace_id}/stats endpoint with credentials."""
    workspace = setup_workspace
    credential = setup_credential

    response = client.get(f"/workspaces/{workspace.id}/stats")
    assert response.status_code == 200

    data = response.json()
    assert data["credential_stats"]["total_credentials"] == 1
    assert len(data["credential_stats"]["recent_credentials"]) == 1
    assert data["credential_stats"]["recent_credentials"][0]["id"] == str(credential.id)
    assert data["credential_stats"]["recent_credentials"][0]["name"] == credential.name
    assert data["credential_stats"]["recent_credentials"][0]["type"] == credential.type


def test_get_workspace_stats_comprehensive(
    client, setup_workspace, setup_project, setup_prompt, setup_plugin, setup_credential
):
    """Test GET /workspaces/{workspace_id}/stats endpoint with all types of data."""
    workspace = setup_workspace
    project = setup_project
    prompt = setup_prompt
    plugin = setup_plugin
    credential = setup_credential

    response = client.get(f"/workspaces/{workspace.id}/stats")
    assert response.status_code == 200

    data = response.json()

    # Check projects
    assert data["project_stats"]["total_projects"] == 1
    assert len(data["project_stats"]["recent_projects"]) == 1
    assert data["project_stats"]["recent_projects"][0]["id"] == str(project.id)

    # Check prompts
    assert data["prompt_stats"]["total_prompts"] == 1
    assert len(data["prompt_stats"]["recent_prompts"]) == 1
    assert data["prompt_stats"]["recent_prompts"][0]["id"] == str(prompt.id)

    # Check plugins
    assert data["plugin_stats"]["total_enabled"] == 0
    assert data["plugin_stats"]["total_disabled"] == 1

    # Check credentials
    assert data["credential_stats"]["total_credentials"] == 1
    assert len(data["credential_stats"]["recent_credentials"]) == 1
    assert data["credential_stats"]["recent_credentials"][0]["id"] == str(credential.id)


def test_get_workspace_stats_multiple_items(client, setup_workspace, db, faker):
    """Test GET /workspaces/{workspace_id}/stats endpoint with multiple items."""
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

    response = client.get(f"/workspaces/{workspace.id}/stats")
    assert response.status_code == 200

    data = response.json()

    # Check counts
    assert data["project_stats"]["total_projects"] == 3
    assert data["prompt_stats"]["total_prompts"] == 3
    assert data["plugin_stats"]["total_enabled"] == 2  # 2 RUNNING plugins
    assert data["plugin_stats"]["total_disabled"] == 1  # 1 STOPPED plugin
    assert data["credential_stats"]["total_credentials"] == 3

    # Check recent items (should be limited to 5 most recent)
    assert len(data["project_stats"]["recent_projects"]) == 3
    assert len(data["prompt_stats"]["recent_prompts"]) == 3
    assert len(data["credential_stats"]["recent_credentials"]) == 3


def test_get_workspace_stats_nonexistent_workspace(client):
    """Test GET /workspaces/{workspace_id}/stats endpoint with nonexistent workspace."""
    import uuid

    nonexistent_id = uuid.uuid4()
    response = client.get(f"/workspaces/{nonexistent_id}/stats")
    assert response.status_code == 404
    assert response.json()["detail"] == "Workspace not found"


def test_get_workspace_stats_different_workspace(client, setup_different_workspace):
    """Test GET /workspaces/{workspace_id}/stats endpoint with a different workspace."""
    workspace = setup_different_workspace

    response = client.get(f"/workspaces/{workspace.id}/stats")
    assert response.status_code == 200

    # Should return empty stats for the different workspace
    data = response.json()
    assert data["project_stats"]["total_projects"] == 0
    assert data["project_stats"]["recent_projects"] == []
    assert data["prompt_stats"]["total_prompts"] == 0
    assert data["prompt_stats"]["recent_prompts"] == []
    assert data["plugin_stats"]["total_enabled"] == 0
    assert data["plugin_stats"]["total_disabled"] == 0
    assert data["credential_stats"]["total_credentials"] == 0
    assert data["credential_stats"]["recent_credentials"] == []
