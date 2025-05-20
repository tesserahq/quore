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


def test_delete_workspace(client, setup_workspace):
    """Test DELETE /workspaces/{workspace_id} endpoint."""
    workspace = setup_workspace
    response = client.delete(f"/workspaces/{workspace.id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Workspace deleted successfully"}

    # Verify the workspace is deleted
    response = client.get(f"/workspaces/{workspace.id}")
    assert response.status_code == 404
