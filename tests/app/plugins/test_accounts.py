import pytest
from app.plugins.accounts import create_account, list_accounts, get_account, update_account, delete_account, _accounts


def setup_function():
    """Clear accounts before each test."""
    _accounts.clear()


def test_create_account_with_valid_name():
    """Test creating an account with a valid name."""
    result = create_account(None, "Test Account", "A test account")
    
    assert result["name"] == "Test Account"
    assert result["description"] == "A test account"
    assert "id" in result
    assert len(_accounts) == 1


def test_create_account_name_required():
    """Test that creating an account without a name raises an error."""
    with pytest.raises(ValueError, match="Account name is required and cannot be empty"):
        create_account(None, "", "A test account")


def test_create_account_name_cannot_be_none():
    """Test that creating an account with None name raises an error."""
    with pytest.raises(ValueError, match="Account name is required and cannot be empty"):
        create_account(None, None, "A test account")


def test_create_account_name_cannot_be_whitespace_only():
    """Test that creating an account with whitespace-only name raises an error."""
    with pytest.raises(ValueError, match="Account name is required and cannot be empty"):
        create_account(None, "   ", "A test account")


def test_create_account_strips_whitespace():
    """Test that account name is properly stripped of leading/trailing whitespace."""
    result = create_account(None, "  Test Account  ", "A test account")
    
    assert result["name"] == "Test Account"


def test_create_account_without_description():
    """Test creating an account without a description."""
    result = create_account(None, "Test Account")
    
    assert result["name"] == "Test Account"
    assert result["description"] is None


def test_list_accounts_empty():
    """Test listing accounts when none exist."""
    result = list_accounts(None)
    assert result == []


def test_list_accounts_with_data():
    """Test listing accounts when some exist."""
    create_account(None, "Account 1", "First account")
    create_account(None, "Account 2", "Second account")
    
    result = list_accounts(None)
    assert len(result) == 2
    assert any(acc["name"] == "Account 1" for acc in result)
    assert any(acc["name"] == "Account 2" for acc in result)


def test_get_account():
    """Test retrieving a specific account."""
    created = create_account(None, "Test Account", "A test account")
    account_id = created["id"]
    
    result = get_account(None, account_id)
    assert result["id"] == account_id
    assert result["name"] == "Test Account"


def test_get_account_not_found():
    """Test retrieving a non-existent account."""
    with pytest.raises(ValueError, match="Account with ID nonexistent not found"):
        get_account(None, "nonexistent")


def test_update_account_name():
    """Test updating an account's name."""
    created = create_account(None, "Original Name", "A test account")
    account_id = created["id"]
    
    result = update_account(None, account_id, name="Updated Name")
    assert result["name"] == "Updated Name"
    assert result["description"] == "A test account"


def test_update_account_name_cannot_be_empty():
    """Test that updating an account with empty name raises an error."""
    created = create_account(None, "Original Name", "A test account")
    account_id = created["id"]
    
    with pytest.raises(ValueError, match="Account name cannot be empty"):
        update_account(None, account_id, name="")


def test_update_account_name_strips_whitespace():
    """Test that updating an account name strips whitespace."""
    created = create_account(None, "Original Name", "A test account")
    account_id = created["id"]
    
    result = update_account(None, account_id, name="  Updated Name  ")
    assert result["name"] == "Updated Name"


def test_update_account_not_found():
    """Test updating a non-existent account."""
    with pytest.raises(ValueError, match="Account with ID nonexistent not found"):
        update_account(None, "nonexistent", name="New Name")


def test_delete_account():
    """Test deleting an account."""
    created = create_account(None, "Test Account", "A test account")
    account_id = created["id"]
    
    result = delete_account(None, account_id)
    assert result["message"] == f"Account {account_id} deleted successfully"
    assert len(_accounts) == 0


def test_delete_account_not_found():
    """Test deleting a non-existent account."""
    with pytest.raises(ValueError, match="Account with ID nonexistent not found"):
        delete_account(None, "nonexistent")


def test_get_tools():
    """Test that get_tools returns the expected tools."""
    from app.plugins.accounts import get_tools
    
    tools = get_tools()
    tool_names = [tool.metadata.name for tool in tools]
    
    expected_tools = ["create_account", "list_accounts", "get_account", "update_account", "delete_account"]
    for expected_tool in expected_tools:
        assert expected_tool in tool_names