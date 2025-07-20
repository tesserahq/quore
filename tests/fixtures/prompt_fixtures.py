import pytest
from app.models.prompt import Prompt


@pytest.fixture
def setup_prompt(db, setup_user, setup_workspace, setup_membership, faker):
    """Create a test prompt in the database with optional overrides."""
    user = setup_user
    workspace = setup_workspace
    _ = setup_membership  # Ensure user has membership in workspace

    prompt_data = {
        "name": faker.word(),
        "prompt_id": faker.uuid4(),
        "type": faker.word(),
        "prompt": faker.text(200),
        "created_by_id": user.id,
        "workspace_id": workspace.id,
    }

    prompt = Prompt(**prompt_data)
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


@pytest.fixture
def setup_different_prompt(
    db, setup_another_user, setup_different_workspace, setup_different_membership, faker
):
    """Create a different test prompt in the database."""
    user = setup_another_user
    workspace = setup_different_workspace
    _ = setup_different_membership  # Ensure user has membership in workspace

    prompt_data = {
        "name": faker.word(),
        "prompt_id": faker.uuid4(),
        "type": faker.word(),
        "prompt": faker.text(200),
        "created_by_id": user.id,
        "workspace_id": workspace.id,
    }

    prompt = Prompt(**prompt_data)
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


@pytest.fixture
def setup_system_prompt(db, setup_user, setup_workspace, setup_membership, faker):
    """Create a system-type test prompt in the database."""
    user = setup_user
    workspace = setup_workspace
    _ = setup_membership  # Ensure user has membership in workspace

    prompt_data = {
        "name": faker.word(),
        "prompt_id": faker.uuid4(),
        "type": "system",
        "prompt": faker.text(200),
        "created_by_id": user.id,
        "workspace_id": workspace.id,
    }

    prompt = Prompt(**prompt_data)
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


@pytest.fixture
def setup_user_prompt(db, setup_user, setup_workspace, setup_membership, faker):
    """Create a user-type test prompt in the database."""
    user = setup_user
    workspace = setup_workspace
    _ = setup_membership  # Ensure user has membership in workspace

    prompt_data = {
        "name": faker.word(),
        "prompt_id": faker.uuid4(),
        "type": "user",
        "prompt": faker.text(200),
        "created_by_id": user.id,
        "workspace_id": workspace.id,
    }

    prompt = Prompt(**prompt_data)
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt
