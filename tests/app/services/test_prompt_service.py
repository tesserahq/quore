import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from app.schemas.prompt import PromptCreate, PromptUpdate
from app.services.prompt_service import PromptService


@pytest.fixture
def sample_prompt_data():
    return {
        "name": "Test Prompt",
        "prompt_id": "test-prompt-001",
        "type": "system",
        "prompt": "This is a test prompt content.",
    }


def test_create_prompt(db: Session, setup_user, setup_workspace, sample_prompt_data):
    """Test creating a new prompt."""
    user = setup_user
    workspace = setup_workspace

    # Create prompt data with required foreign keys
    prompt_data = {
        **sample_prompt_data,
        "created_by_id": user.id,
        "workspace_id": workspace.id,
    }
    prompt_create = PromptCreate(**prompt_data)
    prompt = PromptService(db).create_prompt(prompt_create)

    # Assertions
    assert prompt.id is not None
    assert prompt.name == sample_prompt_data["name"]
    assert prompt.prompt_id == sample_prompt_data["prompt_id"]
    assert prompt.type == sample_prompt_data["type"]
    assert prompt.prompt == sample_prompt_data["prompt"]
    assert prompt.created_by_id == user.id
    assert prompt.workspace_id == workspace.id
    assert prompt.created_at is not None
    assert prompt.updated_at is not None


def test_get_prompt(db: Session, setup_prompt):
    """Test retrieving a single prompt by ID."""
    prompt = setup_prompt

    # Get prompt
    retrieved_prompt = PromptService(db).get_prompt(prompt.id)

    # Assertions
    assert retrieved_prompt is not None
    assert retrieved_prompt.id == prompt.id
    assert retrieved_prompt.name == prompt.name
    assert retrieved_prompt.prompt_id == prompt.prompt_id
    assert retrieved_prompt.type == prompt.type
    assert retrieved_prompt.prompt == prompt.prompt


def test_get_prompt_not_found(db: Session):
    """Test retrieving a non-existent prompt."""
    # Try to get non-existent prompt
    retrieved_prompt = PromptService(db).get_prompt(uuid4())

    # Assertion
    assert retrieved_prompt is None


def test_get_prompt_by_prompt_id(db: Session, setup_prompt):
    """Test retrieving a prompt by prompt_id string."""
    prompt = setup_prompt

    # Get prompt by prompt_id
    retrieved_prompt = PromptService(db).get_prompt_by_prompt_id(prompt.prompt_id)

    # Assertions
    assert retrieved_prompt is not None
    assert retrieved_prompt.id == prompt.id
    assert retrieved_prompt.name == prompt.name
    assert retrieved_prompt.prompt_id == prompt.prompt_id
    assert retrieved_prompt.type == prompt.type
    assert retrieved_prompt.prompt == prompt.prompt


def test_get_prompt_by_prompt_id_not_found(db: Session):
    """Test retrieving a non-existent prompt by prompt_id."""
    # Try to get non-existent prompt by prompt_id
    retrieved_prompt = PromptService(db).get_prompt_by_prompt_id(
        "non-existent-prompt-id"
    )

    # Assertion
    assert retrieved_prompt is None


def test_get_prompt_by_id_or_prompt_id_with_uuid(db: Session, setup_prompt):
    """Test retrieving a prompt by UUID using the flexible method."""
    prompt = setup_prompt

    # Get prompt by UUID
    retrieved_prompt = PromptService(db).get_prompt_by_id_or_prompt_id(prompt.id)

    # Assertions
    assert retrieved_prompt is not None
    assert retrieved_prompt.id == prompt.id
    assert retrieved_prompt.name == prompt.name
    assert retrieved_prompt.prompt_id == prompt.prompt_id
    assert retrieved_prompt.type == prompt.type
    assert retrieved_prompt.prompt == prompt.prompt


def test_get_prompt_by_id_or_prompt_id_with_string(db: Session, setup_prompt):
    """Test retrieving a prompt by string prompt_id using the flexible method."""
    prompt = setup_prompt

    # Get prompt by string prompt_id
    retrieved_prompt = PromptService(db).get_prompt_by_id_or_prompt_id(prompt.prompt_id)

    # Assertions
    assert retrieved_prompt is not None
    assert retrieved_prompt.id == prompt.id
    assert retrieved_prompt.name == prompt.name
    assert retrieved_prompt.prompt_id == prompt.prompt_id
    assert retrieved_prompt.type == prompt.type
    assert retrieved_prompt.prompt == prompt.prompt


def test_get_prompt_by_id_or_prompt_id_not_found(db: Session):
    """Test retrieving a non-existent prompt using the flexible method."""
    # Try to get non-existent prompt by UUID
    retrieved_prompt = PromptService(db).get_prompt_by_id_or_prompt_id(uuid4())
    assert retrieved_prompt is None

    # Try to get non-existent prompt by string
    retrieved_prompt = PromptService(db).get_prompt_by_id_or_prompt_id(
        "non-existent-prompt-id"
    )
    assert retrieved_prompt is None


def test_get_prompt_by_id_or_prompt_id_invalid_type(db: Session):
    """Test that the flexible method raises ValueError for invalid types."""
    with pytest.raises(ValueError, match="Identifier must be UUID or string"):
        PromptService(db).get_prompt_by_id_or_prompt_id(123)  # Invalid type

    with pytest.raises(ValueError, match="Identifier must be UUID or string"):
        PromptService(db).get_prompt_by_id_or_prompt_id(None)  # Invalid type


def test_get_prompts(db: Session, setup_prompt):
    """Test retrieving a list of prompts with pagination."""
    prompt = setup_prompt

    # Get all prompts
    prompts = PromptService(db).get_prompts()

    # Assertions
    assert len(prompts) >= 1
    assert any(p.id == prompt.id for p in prompts)


def test_get_prompts_with_pagination(db: Session, setup_prompt):
    """Test retrieving prompts with pagination parameters."""
    prompt = setup_prompt

    # Get prompts with pagination
    prompts = PromptService(db).get_prompts(skip=0, limit=5)

    # Assertions
    assert len(prompts) <= 5
    assert any(p.id == prompt.id for p in prompts)


def test_update_prompt(db: Session, setup_prompt):
    """Test updating an existing prompt."""
    prompt = setup_prompt

    # Update data
    update_data = {
        "name": "Updated Prompt",
        "type": "user",
        "prompt": "This is an updated prompt content.",
    }
    prompt_update = PromptUpdate(**update_data)

    # Update prompt
    updated_prompt = PromptService(db).update_prompt(prompt.id, prompt_update)

    # Assertions
    assert updated_prompt is not None
    assert updated_prompt.id == prompt.id
    assert updated_prompt.name == update_data["name"]
    assert updated_prompt.type == update_data["type"]
    assert updated_prompt.prompt == update_data["prompt"]
    # Original fields should remain unchanged
    assert updated_prompt.prompt_id == prompt.prompt_id
    assert updated_prompt.created_by_id == prompt.created_by_id
    assert updated_prompt.workspace_id == prompt.workspace_id


def test_update_prompt_not_found(db: Session):
    """Test updating a non-existent prompt."""
    # Try to update non-existent prompt
    update_data = {"name": "Updated Prompt"}
    prompt_update = PromptUpdate(**update_data)

    # Update prompt
    updated_prompt = PromptService(db).update_prompt(uuid4(), prompt_update)

    # Assertion
    assert updated_prompt is None


def test_delete_prompt(db: Session, setup_prompt):
    """Test deleting a prompt."""
    prompt = setup_prompt

    # Delete prompt
    prompt_service = PromptService(db)
    success = prompt_service.delete_prompt(prompt.id)

    # Assertions
    assert success is True
    deleted_prompt = prompt_service.get_prompt(prompt.id)
    assert deleted_prompt is None


def test_delete_prompt_not_found(db: Session):
    """Test deleting a non-existent prompt."""
    # Try to delete non-existent prompt
    success = PromptService(db).delete_prompt(uuid4())

    # Assertion
    assert success is False


def test_search_prompts_with_filters(db: Session, setup_prompt):
    """Test searching prompts with various filters."""
    prompt = setup_prompt

    # Search using ilike filter on name
    filters = {"name": {"operator": "ilike", "value": f"%{prompt.name}%"}}
    results = PromptService(db).search(filters)

    assert isinstance(results, list)
    assert any(result.id == prompt.id for result in results)

    # Search using exact match on type
    filters = {"type": prompt.type}
    results = PromptService(db).search(filters)

    assert len(results) >= 1
    assert any(result.id == prompt.id for result in results)

    # Search with workspace_id filter
    filters = {"workspace_id": prompt.workspace_id}
    results = PromptService(db).search(filters)

    assert len(results) >= 1
    assert any(result.id == prompt.id for result in results)

    # Search with no match
    filters = {"name": {"operator": "==", "value": "Nonexistent Name"}}
    results = PromptService(db).search(filters)

    assert len(results) == 0


def test_get_prompts_by_workspace(db: Session, setup_prompt, setup_different_prompt):
    """Test retrieving prompts filtered by workspace."""
    prompt = setup_prompt
    different_prompt = setup_different_prompt

    # Get prompts for the first workspace
    workspace_prompts = PromptService(db).get_prompts_by_workspace(prompt.workspace_id)

    # Assertions
    assert len(workspace_prompts) >= 1
    assert any(p.id == prompt.id for p in workspace_prompts)
    assert not any(p.id == different_prompt.id for p in workspace_prompts)


def test_get_prompts_by_type(db: Session, setup_system_prompt, setup_user_prompt):
    """Test retrieving prompts filtered by type."""
    system_prompt = setup_system_prompt
    user_prompt = setup_user_prompt

    # Get system prompts
    system_prompts = PromptService(db).get_prompts_by_type("system")

    # Assertions
    assert len(system_prompts) >= 1
    assert any(p.id == system_prompt.id for p in system_prompts)
    assert not any(p.id == user_prompt.id for p in system_prompts)

    # Get user prompts
    user_prompts = PromptService(db).get_prompts_by_type("user")

    # Assertions
    assert len(user_prompts) >= 1
    assert any(p.id == user_prompt.id for p in user_prompts)
    assert not any(p.id == system_prompt.id for p in user_prompts)


def test_get_prompts_by_type_with_workspace_filter(
    db: Session, setup_system_prompt, setup_different_prompt
):
    """Test retrieving prompts by type with workspace filter."""
    system_prompt = setup_system_prompt
    different_prompt = setup_different_prompt

    # Get system prompts for the specific workspace
    workspace_system_prompts = PromptService(db).get_prompts_by_type(
        "system", workspace_id=system_prompt.workspace_id
    )

    # Assertions
    assert len(workspace_system_prompts) >= 1
    assert any(p.id == system_prompt.id for p in workspace_system_prompts)
    assert not any(p.id == different_prompt.id for p in workspace_system_prompts)


def test_get_prompts_by_creator(db: Session, setup_prompt, setup_different_prompt):
    """Test retrieving prompts filtered by creator."""
    prompt = setup_prompt
    different_prompt = setup_different_prompt

    # Get prompts created by the first user
    creator_prompts = PromptService(db).get_prompts_by_creator(prompt.created_by_id)

    # Assertions
    assert len(creator_prompts) >= 1
    assert any(p.id == prompt.id for p in creator_prompts)
    assert not any(p.id == different_prompt.id for p in creator_prompts)


def test_get_prompts_by_creator_with_workspace_filter(
    db: Session, setup_prompt, setup_different_prompt
):
    """Test retrieving prompts by creator with workspace filter."""
    prompt = setup_prompt
    different_prompt = setup_different_prompt

    # Get prompts created by the first user in the specific workspace
    creator_workspace_prompts = PromptService(db).get_prompts_by_creator(
        prompt.created_by_id, workspace_id=prompt.workspace_id
    )

    # Assertions
    assert len(creator_workspace_prompts) >= 1
    assert any(p.id == prompt.id for p in creator_workspace_prompts)
    assert not any(p.id == different_prompt.id for p in creator_workspace_prompts)


def test_prompt_pagination(db: Session, setup_prompt):
    """Test pagination functionality in prompt retrieval methods."""
    prompt = setup_prompt

    # Test pagination in get_prompts
    prompts = PromptService(db).get_prompts(skip=0, limit=1)
    assert len(prompts) <= 1

    # Test pagination in get_prompts_by_workspace
    workspace_prompts = PromptService(db).get_prompts_by_workspace(
        prompt.workspace_id, skip=0, limit=1
    )
    assert len(workspace_prompts) <= 1

    # Test pagination in get_prompts_by_type
    type_prompts = PromptService(db).get_prompts_by_type(prompt.type, skip=0, limit=1)
    assert len(type_prompts) <= 1

    # Test pagination in get_prompts_by_creator
    creator_prompts = PromptService(db).get_prompts_by_creator(
        prompt.created_by_id, skip=0, limit=1
    )
    assert len(creator_prompts) <= 1
