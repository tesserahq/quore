from uuid import uuid4
from app.constants.credentials import CredentialType


def test_list_credential_types(client, setup_workspace):
    """Test GET /workspaces/{workspace_id}/credentials/types endpoint."""
    workspace = setup_workspace

    response = client.get(f"/workspaces/{workspace.id}/credentials/types")
    assert response.status_code == 200
    data = response.json()

    # Verify we get a list of credential types
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify each credential type has the expected structure
    for cred_type in data:
        assert "type_name" in cred_type
        assert "display_name" in cred_type
        assert "fields" in cred_type
        assert isinstance(cred_type["fields"], list)

        # Verify fields have the expected structure
        for field in cred_type["fields"]:
            assert "name" in field
            assert "label" in field
            assert "type" in field
            assert "input_type" in field
            assert "required" in field

    # Verify specific credential types are present
    type_names = {cred_type["type_name"] for cred_type in data}
    assert CredentialType.GITHUB_PAT in type_names
    assert CredentialType.GITLAB_PAT in type_names
    assert CredentialType.SSH_KEY in type_names


def test_list_credentials(client, setup_credential, setup_workspace):
    """Test GET /workspaces/{workspace_id}/credentials endpoint."""
    credential = setup_credential
    workspace = setup_workspace

    response = client.get(f"/workspaces/{workspace.id}/credentials")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

    # Make sure the response contains the correct credential
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["id"] == str(credential.id)
    assert item["name"] == credential.name
    assert item["type"] == credential.type
    assert item["workspace_id"] == str(workspace.id)
    assert item["created_by"]["id"] == str(credential.created_by_id)


def test_create_credential(client, setup_workspace, test_credential_data):
    """Test POST /workspaces/{workspace_id}/credentials endpoint."""
    workspace = setup_workspace

    response = client.post(
        f"/workspaces/{workspace.id}/credentials", json=test_credential_data
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_credential_data["name"]
    assert data["type"] == test_credential_data["type"]
    assert data["workspace_id"] == str(workspace.id)


def test_create_credential_invalid_workspace(client, test_credential_data):
    """Test POST /workspaces/{workspace_id}/credentials with invalid workspace."""
    nonexistent_workspace_id = uuid4()

    response = client.post(
        f"/workspaces/{nonexistent_workspace_id}/credentials", json=test_credential_data
    )
    assert response.status_code == 404
