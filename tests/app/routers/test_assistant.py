import uuid


def test_init_assistant_returns_session_id(client, setup_project):
    """Test POST /projects/{project_id}/assistant/init returns a session_id."""
    project = setup_project

    response = client.post(f"/projects/{project.id}/assistant/init")

    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data

    # Validate it's a proper UUID string
    parsed = uuid.UUID(data["session_id"])  # will raise if invalid
    assert str(parsed) == data["session_id"]


def test_init_assistant_nonexistent_project(client):
    """Test POST /projects/{project_id}/assistant/init with non-existent project."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"

    response = client.post(f"/projects/{non_existent_id}/assistant/init")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
