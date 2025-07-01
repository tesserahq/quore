from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from fastmcp import Context
from uuid import uuid4, UUID


class Account(BaseModel):
    """Account model with required name field."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., description="The account name (required)")
    description: Optional[str] = Field(None, description="Optional account description")


class CreateAccountRequest(BaseModel):
    """Request model for creating an account."""
    name: str = Field(..., description="The account name (required)")
    description: Optional[str] = Field(None, description="Optional account description")


# In-memory storage for demonstration (in production, this would use a database)
_accounts: Dict[str, Account] = {}

plugin_app = FastMCP("accounts")


def get_tools():
    """Get all account tools for integration with the system."""
    from llama_index.core.tools import FunctionTool
    
    def create_account_tool(name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new account with required name validation."""
        return create_account(None, name, description)
    
    def list_accounts_tool() -> List[Dict[str, Any]]:
        """List all accounts."""
        return list_accounts(None)
    
    def get_account_tool(account_id: str) -> Dict[str, Any]:
        """Get an account by ID."""
        return get_account(None, account_id)
    
    def update_account_tool(account_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing account."""
        return update_account(None, account_id, name, description)
    
    def delete_account_tool(account_id: str) -> Dict[str, str]:
        """Delete an account by ID."""
        return delete_account(None, account_id)
    
    return [
        FunctionTool.from_defaults(
            fn=create_account_tool,
            name="create_account",
            description="Create a new account (name is required)"
        ),
        FunctionTool.from_defaults(
            fn=list_accounts_tool,
            name="list_accounts",
            description="List all accounts"
        ),
        FunctionTool.from_defaults(
            fn=get_account_tool,
            name="get_account",
            description="Get an account by ID"
        ),
        FunctionTool.from_defaults(
            fn=update_account_tool,
            name="update_account",
            description="Update an existing account"
        ),
        FunctionTool.from_defaults(
            fn=delete_account_tool,
            name="delete_account",
            description="Delete an account by ID"
        ),
    ]


@plugin_app.tool()
def list_accounts(context: Context) -> List[Dict[str, Any]]:
    """List all accounts."""
    return [account.model_dump() for account in _accounts.values()]


@plugin_app.tool()
def create_account(context: Context, name: Optional[str], description: Optional[str] = None) -> Dict[str, Any]:
    """Create a new account.
    
    Args:
        name: The account name (required)
        description: Optional account description
        
    Returns:
        The created account
        
    Raises:
        ValueError: If name is empty or not provided
    """
    if not name or not name.strip():
        raise ValueError("Account name is required and cannot be empty")
    
    account = Account(name=name.strip(), description=description)
    _accounts[account.id] = account
    
    return account.model_dump()


@plugin_app.tool()
def get_account(context: Context, account_id: str) -> Dict[str, Any]:
    """Get an account by ID.
    
    Args:
        account_id: The ID of the account to retrieve
        
    Returns:
        The account data
        
    Raises:
        ValueError: If account not found
    """
    if account_id not in _accounts:
        raise ValueError(f"Account with ID {account_id} not found")
    
    return _accounts[account_id].model_dump()


@plugin_app.tool()
def update_account(context: Context, account_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """Update an existing account.
    
    Args:
        account_id: The ID of the account to update
        name: New account name (optional)
        description: New account description (optional)
        
    Returns:
        The updated account
        
    Raises:
        ValueError: If account not found or name is empty
    """
    if account_id not in _accounts:
        raise ValueError(f"Account with ID {account_id} not found")
    
    account = _accounts[account_id]
    
    if name is not None:
        if not name.strip():
            raise ValueError("Account name cannot be empty")
        account.name = name.strip()
    
    if description is not None:
        account.description = description
    
    return account.model_dump()


@plugin_app.tool()
def delete_account(context: Context, account_id: str) -> Dict[str, str]:
    """Delete an account by ID.
    
    Args:
        account_id: The ID of the account to delete
        
    Returns:
        Success message
        
    Raises:
        ValueError: If account not found
    """
    if account_id not in _accounts:
        raise ValueError(f"Account with ID {account_id} not found")
    
    del _accounts[account_id]
    
    return {"message": f"Account {account_id} deleted successfully"}