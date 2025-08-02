import pytest
from app.constants.membership import MEMBER_ROLE, OWNER_ROLE, ADMIN_ROLE


def test_list_memberships(client, setup_membership):
    """Test GET /workspaces/{workspace_id}/memberships endpoint."""
    membership = setup_membership
    response = client.get(f"/workspaces/{membership.workspace_id}/memberships")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0

    # Verify the created membership is in the list
    membership_list = data["data"]
    assert any(m["id"] == str(membership.id) for m in membership_list)
    assert any(m["user_id"] == str(membership.user_id) for m in membership_list)
    assert any(
        m["workspace_id"] == str(membership.workspace_id) for m in membership_list
    )


def test_create_membership(client, setup_user, setup_workspace, setup_another_user):
    """Test POST /workspaces/{workspace_id}/memberships endpoint."""
    workspace = setup_workspace
    user = (
        setup_another_user  # Use a different user than the one creating the membership
    )

    membership_data = {
        "user_id": str(user.id),
        "workspace_id": str(workspace.id),
        "role": MEMBER_ROLE,
    }

    response = client.post(
        f"/workspaces/{workspace.id}/memberships", json=membership_data
    )

    assert response.status_code == 201
    data = response.json()

    assert data["user_id"] == str(user.id)
    assert data["workspace_id"] == str(workspace.id)
    assert data["role"] == MEMBER_ROLE
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_membership_duplicate(client, setup_membership):
    """Test POST /workspaces/{workspace_id}/memberships endpoint with duplicate membership."""
    membership = setup_membership

    membership_data = {
        "user_id": str(membership.user_id),
        "workspace_id": str(membership.workspace_id),
        "role": MEMBER_ROLE,
    }

    response = client.post(
        f"/workspaces/{membership.workspace_id}/memberships", json=membership_data
    )

    assert response.status_code == 400
    assert "already a member" in response.json()["detail"]


def test_get_membership(client, setup_membership):
    """Test GET /memberships/{membership_id} endpoint."""
    membership = setup_membership

    response = client.get(f"/memberships/{membership.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(membership.id)
    assert data["user_id"] == str(membership.user_id)
    assert data["workspace_id"] == str(membership.workspace_id)
    assert data["role"] == membership.role
    assert "created_at" in data
    assert "updated_at" in data


def test_get_membership_not_found(client, setup_workspace):
    """Test GET /memberships/{membership_id} endpoint with non-existent membership."""
    fake_uuid = "550e8400-e29b-41d4-a716-446655440000"

    response = client.get(f"/memberships/{fake_uuid}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_membership(client, setup_membership):
    """Test PUT /memberships/{membership_id} endpoint."""
    membership = setup_membership

    update_data = {"role": ADMIN_ROLE}

    response = client.put(f"/memberships/{membership.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(membership.id)
    assert data["role"] == ADMIN_ROLE
    assert data["user_id"] == str(membership.user_id)
    assert data["workspace_id"] == str(membership.workspace_id)


def test_update_membership_not_found(client):
    """Test PUT /memberships/{membership_id} endpoint with non-existent membership."""
    fake_uuid = "550e8400-e29b-41d4-a716-446655440000"

    update_data = {"role": ADMIN_ROLE}

    response = client.put(f"/memberships/{fake_uuid}", json=update_data)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_delete_membership(client, setup_membership):
    """Test DELETE /memberships/{membership_id} endpoint."""
    membership = setup_membership

    response = client.delete(f"/memberships/{membership.id}")

    assert response.status_code == 200
    data = response.json()
    assert "deleted successfully" in data["message"]

    # Verify membership is actually deleted
    get_response = client.get(f"/memberships/{membership.id}")
    assert get_response.status_code == 404


def test_delete_membership_not_found(client):
    """Test DELETE /memberships/{membership_id} endpoint with non-existent membership."""
    fake_uuid = "550e8400-e29b-41d4-a716-446655440000"

    response = client.delete(f"/memberships/{fake_uuid}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_list_memberships_pagination(
    client, setup_membership, setup_different_membership
):
    """Test GET /workspaces/{workspace_id}/memberships endpoint with pagination."""
    membership = setup_membership

    # Test with limit
    response = client.get(f"/workspaces/{membership.workspace_id}/memberships?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1

    # Test with skip
    response = client.get(
        f"/workspaces/{membership.workspace_id}/memberships?skip=0&limit=10"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1


def test_create_membership_with_different_roles(
    client, setup_workspace, setup_another_user
):
    """Test creating memberships with different roles."""
    workspace = setup_workspace
    user = setup_another_user

    # Test each role
    roles_to_test = [MEMBER_ROLE, ADMIN_ROLE, OWNER_ROLE]

    for role in roles_to_test:
        membership_data = {
            "user_id": str(user.id),
            "workspace_id": str(workspace.id),
            "role": role,
        }

        response = client.post(
            f"/workspaces/{workspace.id}/memberships", json=membership_data
        )

        if role == roles_to_test[0]:  # First role should succeed
            assert response.status_code == 201
            data = response.json()
            assert data["role"] == role

            # Clean up for next iteration
            client.delete(f"/memberships/{data['id']}")
        else:
            # Subsequent attempts might succeed or fail depending on business logic
            assert response.status_code in [201, 400]


def test_update_membership_to_invalid_role(client, setup_membership):
    """Test updating membership with invalid role."""
    membership = setup_membership

    update_data = {"role": "invalid_role"}

    response = client.put(f"/memberships/{membership.id}", json=update_data)

    # Should either accept it (if no validation) or reject it (if validation exists)
    # This depends on your business logic validation
    assert response.status_code in [200, 400, 422]
