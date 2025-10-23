from uuid import uuid4


def test_list_workspace_prompts(client, setup_prompt, setup_workspace):
    """Test GET /workspaces/{workspace_id}/prompts endpoint."""
    prompt = setup_prompt
    workspace = setup_workspace

    response = client.get(f"/workspaces/{workspace.id}/prompts")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)

    # Make sure the response contains the correct prompt
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == str(prompt.id)
    assert data["data"][0]["name"] == prompt.name
    assert data["data"][0]["prompt_id"] == prompt.prompt_id
    assert data["data"][0]["type"] == prompt.type
    assert data["data"][0]["prompt"] == prompt.prompt
    assert data["data"][0]["workspace_id"] == str(workspace.id)
    assert data["data"][0]["created_by_id"] == str(prompt.created_by_id)


def test_get_workspace_prompt(client, setup_prompt, setup_workspace):
    """Test GET /workspaces/{workspace_id}/prompts/{prompt_id} endpoint."""
    prompt = setup_prompt
    workspace = setup_workspace

    response = client.get(f"/workspaces/{workspace.id}/prompts/{prompt.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(prompt.id)
    assert data["name"] == prompt.name
    assert data["prompt_id"] == prompt.prompt_id
    assert data["type"] == prompt.type
    assert data["prompt"] == prompt.prompt
    assert data["workspace_id"] == str(workspace.id)
    assert data["created_by_id"] == str(prompt.created_by_id)


def test_get_prompt(client, setup_prompt):
    """Test GET /prompts/{prompt_id} endpoint."""
    prompt = setup_prompt

    response = client.get(f"/prompts/{prompt.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(prompt.id)
    assert data["name"] == prompt.name
    assert data["prompt_id"] == prompt.prompt_id
    assert data["type"] == prompt.type
    assert data["prompt"] == prompt.prompt


def test_create_workspace_prompt(client, setup_workspace, setup_user):
    """Test POST /workspaces/{workspace_id}/prompts endpoint."""
    workspace = setup_workspace
    user = setup_user

    prompt_data = {
        "name": "Test System Prompt",
        "prompt_id": "test-system-001",
        "type": "system",
        "prompt": "You are a helpful AI assistant.",
    }

    response = client.post(f"/workspaces/{workspace.id}/prompts", json=prompt_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == prompt_data["name"]
    assert data["prompt_id"] == prompt_data["prompt_id"]
    assert data["type"] == prompt_data["type"]
    assert data["prompt"] == prompt_data["prompt"]
    assert data["workspace_id"] == str(workspace.id)
    assert data["created_by_id"] == str(user.id)


def test_update_workspace_prompt(client, setup_prompt, setup_workspace):
    """Test PUT /workspaces/{workspace_id}/prompts/{prompt_id} endpoint."""
    prompt = setup_prompt
    workspace = setup_workspace

    update_data = {
        "name": "Updated System Prompt",
        "type": "user",
        "prompt": "You are an updated AI assistant.",
        "notes": "This is an updated note.",
    }

    response = client.put(
        f"/workspaces/{workspace.id}/prompts/{prompt.id}", json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["type"] == update_data["type"]
    assert data["prompt"] == update_data["prompt"]
    assert data["id"] == str(prompt.id)
    assert data["workspace_id"] == str(workspace.id)
    # Original fields should remain unchanged
    assert data["prompt_id"] == prompt.prompt_id
    assert data["created_by_id"] == str(prompt.created_by_id)
    assert data["notes"] == update_data["notes"]


def test_update_prompt(client, setup_prompt):
    """Test PUT /prompts/{prompt_id} endpoint."""
    prompt = setup_prompt

    update_data = {
        "name": "Updated Prompt",
        "prompt": "This is an updated prompt content.",
    }

    response = client.put(f"/prompts/{prompt.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["prompt"] == update_data["prompt"]
    assert data["id"] == str(prompt.id)


def test_delete_prompt(client, setup_prompt):
    """Test DELETE /prompts/{prompt_id} endpoint."""
    prompt = setup_prompt

    response = client.delete(f"/prompts/{prompt.id}")
    assert response.status_code == 204

    # Verify the prompt is deleted
    response = client.get(f"/prompts/{prompt.id}")
    assert response.status_code == 404


def test_list_prompts_by_type(
    client, setup_system_prompt, setup_user_prompt, setup_workspace
):
    """Test GET /workspaces/{workspace_id}/prompts/types/{prompt_type} endpoint."""
    system_prompt = setup_system_prompt
    user_prompt = setup_user_prompt
    workspace = setup_workspace

    # Test system prompts
    response = client.get(f"/workspaces/{workspace.id}/prompts/types/system")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == str(system_prompt.id)
    assert data["data"][0]["type"] == "system"

    # Test user prompts
    response = client.get(f"/workspaces/{workspace.id}/prompts/types/user")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == str(user_prompt.id)
    assert data["data"][0]["type"] == "user"


def test_list_prompts_by_creator(client, setup_prompt, setup_workspace):
    """Test GET /workspaces/{workspace_id}/prompts/creator/{creator_id} endpoint."""
    prompt = setup_prompt
    workspace = setup_workspace

    response = client.get(
        f"/workspaces/{workspace.id}/prompts/creator/{prompt.created_by_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == str(prompt.id)
    assert data["data"][0]["created_by_id"] == str(prompt.created_by_id)


def test_pagination(client, setup_prompt, setup_workspace):
    """Test pagination parameters on list endpoints."""
    prompt = setup_prompt
    workspace = setup_workspace

    # Test pagination on workspace prompts
    response = client.get(f"/workspaces/{workspace.id}/prompts?skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) <= 5

    # Test pagination on prompts by type
    response = client.get(
        f"/workspaces/{workspace.id}/prompts/types/{prompt.type}?skip=0&limit=5"
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) <= 5

    # Test pagination on prompts by creator
    response = client.get(
        f"/workspaces/{workspace.id}/prompts/creator/{prompt.created_by_id}?skip=0&limit=5"
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) <= 5


# Error cases and edge cases


def test_get_nonexistent_workspace_prompt(client, setup_workspace):
    """Test GET /workspaces/{workspace_id}/prompts/{prompt_id} with non-existent prompt."""
    workspace = setup_workspace
    nonexistent_id = uuid4()

    response = client.get(f"/workspaces/{workspace.id}/prompts/{nonexistent_id}")
    assert response.status_code == 404


def test_get_nonexistent_prompt(client):
    """Test GET /prompts/{prompt_id} with non-existent prompt."""
    nonexistent_id = uuid4()

    response = client.get(f"/prompts/{nonexistent_id}")
    assert response.status_code == 404


def test_create_prompt_invalid_workspace(client, setup_user):
    """Test POST /workspaces/{workspace_id}/prompts with invalid workspace."""
    user = setup_user
    nonexistent_workspace_id = uuid4()

    prompt_data = {
        "name": "Test Prompt",
        "prompt_id": "test-001",
        "type": "system",
        "prompt": "Test content.",
    }

    response = client.post(
        f"/workspaces/{nonexistent_workspace_id}/prompts", json=prompt_data
    )
    assert response.status_code == 404


def test_update_nonexistent_workspace_prompt(client, setup_workspace):
    """Test PUT /workspaces/{workspace_id}/prompts/{prompt_id} with non-existent prompt."""
    workspace = setup_workspace
    nonexistent_id = uuid4()

    update_data = {
        "name": "Updated Prompt",
        "prompt": "Updated content.",
    }

    response = client.put(
        f"/workspaces/{workspace.id}/prompts/{nonexistent_id}", json=update_data
    )
    assert response.status_code == 404


def test_update_nonexistent_prompt(client):
    """Test PUT /prompts/{prompt_id} with non-existent prompt."""
    nonexistent_id = uuid4()

    update_data = {
        "name": "Updated Prompt",
        "prompt": "Updated content.",
    }

    response = client.put(f"/prompts/{nonexistent_id}", json=update_data)
    assert response.status_code == 404


def test_delete_nonexistent_prompt(client):
    """Test DELETE /prompts/{prompt_id} with non-existent prompt."""
    nonexistent_id = uuid4()

    response = client.delete(f"/prompts/{nonexistent_id}")
    assert response.status_code == 404


def test_create_prompt_invalid_data(client, setup_workspace):
    """Test POST /workspaces/{workspace_id}/prompts with invalid data."""
    workspace = setup_workspace

    # Missing required fields
    invalid_prompt_data = {
        "name": "Test Prompt",
        # Missing prompt_id, type, and prompt
    }

    response = client.post(
        f"/workspaces/{workspace.id}/prompts", json=invalid_prompt_data
    )
    assert response.status_code == 422  # Validation error

    # Empty required fields
    invalid_prompt_data = {
        "name": "",
        "prompt_id": "",
        "type": "",
        "prompt": "",
    }

    response = client.post(
        f"/workspaces/{workspace.id}/prompts", json=invalid_prompt_data
    )
    assert response.status_code == 422  # Validation error


def test_update_prompt_invalid_data(client, setup_prompt, setup_workspace):
    """Test PUT /workspaces/{workspace_id}/prompts/{prompt_id} with invalid data."""
    prompt = setup_prompt
    workspace = setup_workspace

    # Empty name
    invalid_update_data = {
        "name": "",
        "prompt": "Valid prompt content.",
    }

    response = client.put(
        f"/workspaces/{workspace.id}/prompts/{prompt.id}", json=invalid_update_data
    )
    assert response.status_code == 422  # Validation error

    # Empty prompt
    invalid_update_data = {
        "name": "Valid name",
        "prompt": "",
    }

    response = client.put(
        f"/workspaces/{workspace.id}/prompts/{prompt.id}", json=invalid_update_data
    )
    assert response.status_code == 422  # Validation error


def test_cross_workspace_access_denied(client, setup_prompt, setup_different_workspace):
    """Test that prompts cannot be accessed from different workspaces."""
    prompt = setup_prompt
    different_workspace = setup_different_workspace

    # Try to access prompt from different workspace
    response = client.get(f"/workspaces/{different_workspace.id}/prompts/{prompt.id}")
    assert response.status_code == 404

    # Try to update prompt from different workspace
    update_data = {
        "name": "Unauthorized Update",
        "prompt": "Unauthorized content.",
    }
    response = client.put(
        f"/workspaces/{different_workspace.id}/prompts/{prompt.id}", json=update_data
    )
    assert response.status_code == 404


def test_workspace_isolation(
    client,
    setup_prompt,
    setup_different_prompt,
    setup_workspace,
    setup_different_workspace,
):
    """Test that prompts are properly isolated between workspaces."""
    prompt = setup_prompt
    different_prompt = setup_different_prompt
    workspace = setup_workspace
    different_workspace = setup_different_workspace

    # List prompts in first workspace
    response = client.get(f"/workspaces/{workspace.id}/prompts")
    assert response.status_code == 200
    data = response.json()
    workspace_prompts = [p["id"] for p in data["data"]]
    assert str(prompt.id) in workspace_prompts
    assert str(different_prompt.id) not in workspace_prompts

    # List prompts in second workspace
    response = client.get(f"/workspaces/{different_workspace.id}/prompts")
    assert response.status_code == 200
    data = response.json()
    different_workspace_prompts = [p["id"] for p in data["data"]]
    assert str(different_prompt.id) in different_workspace_prompts
    assert str(prompt.id) not in different_workspace_prompts
