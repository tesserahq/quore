import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


def test_create_app_setting(client):
    """Test POST /app-settings endpoint."""
    response = client.post(
        "/app-settings",
        json={"key": "test_setting", "value": "test_value"},
    )
    assert response.status_code == 201
    app_setting = response.json()
    assert app_setting["key"] == "test_setting"
    assert app_setting["value"] == "test_value"
    assert "id" in app_setting
    assert "created_at" in app_setting
    assert "updated_at" in app_setting


def test_create_app_setting_duplicate_key(client):
    """Test POST /app-settings endpoint with duplicate key."""
    # Create first app setting
    client.post(
        "/app-settings",
        json={"key": "duplicate_key", "value": "first_value"},
    )

    # Try to create another with same key
    response = client.post(
        "/app-settings",
        json={"key": "duplicate_key", "value": "second_value"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_list_app_settings(client):
    """Test GET /app-settings endpoint."""
    # Create some test data
    client.post("/app-settings", json={"key": "setting1", "value": "value1"})
    client.post("/app-settings", json={"key": "setting2", "value": "value2"})

    response = client.get("/app-settings")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 2


def test_list_app_settings_with_pagination(client):
    """Test GET /app-settings endpoint with pagination."""
    # Create some test data
    for i in range(5):
        client.post(
            "/app-settings", json={"key": f"setting_{i}", "value": f"value_{i}"}
        )

    response = client.get("/app-settings?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) <= 2


def test_get_app_setting_by_id(client):
    """Test GET /app-settings/{id} endpoint with UUID."""
    # Create an app setting
    create_response = client.post(
        "/app-settings",
        json={"key": "test_get", "value": "test_value"},
    )
    app_setting_id = create_response.json()["id"]

    # Get the app setting by ID
    response = client.get(f"/app-settings/{app_setting_id}")
    assert response.status_code == 200
    app_setting = response.json()
    assert app_setting["id"] == app_setting_id
    assert app_setting["key"] == "test_get"
    assert app_setting["value"] == "test_value"


def test_get_app_setting_by_key(client):
    """Test GET /app-settings/{key} endpoint with key."""
    # Create an app setting
    client.post(
        "/app-settings",
        json={"key": "test_key", "value": "test_value"},
    )

    # Get the app setting by key
    response = client.get("/app-settings/test_key")
    assert response.status_code == 200
    app_setting = response.json()
    assert app_setting["key"] == "test_key"
    assert app_setting["value"] == "test_value"


def test_get_app_setting_not_found(client):
    """Test GET /app-settings/{id_or_key} endpoint with non-existent ID/key."""
    # Test with non-existent UUID
    non_existent_id = uuid4()
    response = client.get(f"/app-settings/{non_existent_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

    # Test with non-existent key
    response = client.get("/app-settings/non_existent_key")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_app_setting(client):
    """Test PUT /app-settings/{id} endpoint."""
    # Create an app setting
    create_response = client.post(
        "/app-settings",
        json={"key": "test_update", "value": "original_value"},
    )
    app_setting_id = create_response.json()["id"]

    # Update the app setting
    response = client.put(
        f"/app-settings/{app_setting_id}",
        json={"key": "updated_key", "value": "updated_value"},
    )
    assert response.status_code == 200
    app_setting = response.json()
    assert app_setting["id"] == app_setting_id
    assert app_setting["key"] == "updated_key"
    assert app_setting["value"] == "updated_value"


def test_update_app_setting_partial(client):
    """Test PUT /app-settings/{id} endpoint with partial update."""
    # Create an app setting
    create_response = client.post(
        "/app-settings",
        json={"key": "test_partial", "value": "original_value"},
    )
    app_setting_id = create_response.json()["id"]

    # Update only the value
    response = client.put(
        f"/app-settings/{app_setting_id}",
        json={"value": "updated_value_only"},
    )
    assert response.status_code == 200
    app_setting = response.json()
    assert app_setting["id"] == app_setting_id
    assert app_setting["key"] == "test_partial"  # Should remain unchanged
    assert app_setting["value"] == "updated_value_only"


def test_update_app_setting_duplicate_key(client):
    """Test PUT /app-settings/{id} endpoint with duplicate key."""
    # Create two app settings
    create_response1 = client.post(
        "/app-settings",
        json={"key": "key1", "value": "value1"},
    )
    client.post(
        "/app-settings",
        json={"key": "key2", "value": "value2"},
    )

    app_setting_id = create_response1.json()["id"]

    # Try to update first setting to use second setting's key
    response = client.put(
        f"/app-settings/{app_setting_id}",
        json={"key": "key2", "value": "new_value"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_update_app_setting_not_found(client):
    """Test PUT /app-settings/{id} endpoint with non-existent ID."""
    non_existent_id = uuid4()
    response = client.put(
        f"/app-settings/{non_existent_id}",
        json={"value": "updated_value"},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_delete_app_setting(client):
    """Test DELETE /app-settings/{id} endpoint."""
    # Create an app setting
    create_response = client.post(
        "/app-settings",
        json={"key": "test_delete", "value": "test_value"},
    )
    app_setting_id = create_response.json()["id"]

    # Delete the app setting
    response = client.delete(f"/app-settings/{app_setting_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/app-settings/{app_setting_id}")
    assert get_response.status_code == 404


def test_delete_app_setting_not_found(client):
    """Test DELETE /app-settings/{id} endpoint with non-existent ID."""
    non_existent_id = uuid4()
    response = client.delete(f"/app-settings/{non_existent_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_app_setting_validation(client):
    """Test app setting validation."""
    # Test missing required fields
    response = client.post("/app-settings", json={})
    assert response.status_code == 422  # Validation error

    # Test missing key
    response = client.post("/app-settings", json={"value": "test_value"})
    assert response.status_code == 422

    # Test missing value
    response = client.post("/app-settings", json={"key": "test_key"})
    assert response.status_code == 422


def test_app_setting_timestamps(client):
    """Test that timestamps are properly set."""
    response = client.post(
        "/app-settings",
        json={"key": "timestamp_test", "value": "test_value"},
    )
    assert response.status_code == 201
    app_setting = response.json()

    # Check that timestamps are present and are strings (ISO format)
    assert "created_at" in app_setting
    assert "updated_at" in app_setting
    assert isinstance(app_setting["created_at"], str)
    assert isinstance(app_setting["updated_at"], str)

    # Check that created_at and updated_at are very close (within 1 second)
    from datetime import datetime

    created_at = datetime.fromisoformat(
        app_setting["created_at"].replace("Z", "+00:00")
    )
    updated_at = datetime.fromisoformat(
        app_setting["updated_at"].replace("Z", "+00:00")
    )
    time_diff = abs((updated_at - created_at).total_seconds())
    assert time_diff < 1.0  # Should be within 1 second
