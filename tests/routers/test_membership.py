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
