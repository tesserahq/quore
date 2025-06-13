import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.services.workspace import WorkspaceService


@pytest.fixture
def sample_workspace_data():
    return {"name": "Test Workspace", "description": "A test workspace"}


def test_create_workspace(db: Session, setup_user, sample_workspace_data):
    # Create workspace
    user = setup_user
    sample_workspace_data = {**sample_workspace_data, "created_by_id": user.id}
    workspace_create = WorkspaceCreate(**sample_workspace_data)
    workspace = WorkspaceService(db).create_workspace(workspace_create)

    # Assertions
    assert workspace.id is not None
    assert workspace.name == sample_workspace_data["name"]
    assert workspace.description == sample_workspace_data["description"]
    assert workspace.created_by_id == sample_workspace_data["created_by_id"]
    assert workspace.created_at is not None
    assert workspace.updated_at is not None


def test_get_workspace(db: Session, setup_workspace):
    workspace = setup_workspace

    # Get workspace
    retrieved_workspace = WorkspaceService(db).get_workspace(workspace.id)

    # Assertions
    assert retrieved_workspace is not None
    assert retrieved_workspace.id == workspace.id
    assert retrieved_workspace.name == workspace.name


def test_get_workspace_not_found(db: Session):
    # Try to get non-existent workspace
    retrieved_workspace = WorkspaceService(db).get_workspace(uuid4())

    # Assertion
    assert retrieved_workspace is None


def test_get_workspaces(db: Session, setup_workspace):
    workspace = setup_workspace

    # Get all workspaces
    workspaces = WorkspaceService(db).get_workspaces()

    # Assertions
    assert len(workspaces) >= 1
    assert any(w.id == workspace.id for w in workspaces)


def test_update_workspace(db: Session, setup_workspace):
    workspace = setup_workspace

    # Update data
    update_data = {"name": "Updated Workspace", "description": "Updated description"}
    workspace_update = WorkspaceUpdate(**update_data)

    # Update workspace
    updated_workspace = WorkspaceService(db).update_workspace(
        workspace.id, workspace_update
    )

    # Assertions
    assert updated_workspace is not None
    assert updated_workspace.id == workspace.id
    assert updated_workspace.name == update_data["name"]
    assert updated_workspace.description == update_data["description"]


def test_update_workspace_not_found(db: Session):
    # Try to update non-existent workspace
    update_data = {"name": "Updated Workspace"}
    workspace_update = WorkspaceUpdate(**update_data)

    # Update workspace
    updated_workspace = WorkspaceService(db).update_workspace(uuid4(), workspace_update)

    # Assertion
    assert updated_workspace is None


def test_delete_workspace(db: Session, setup_workspace):
    workspace = setup_workspace

    # Delete workspace
    workspace_service = WorkspaceService(db)
    success = workspace_service.delete_workspace(workspace.id)

    # Assertions
    assert success is True
    deleted_workspace = workspace_service.get_workspace(workspace.id)
    assert deleted_workspace is None


def test_delete_workspace_not_found(db: Session):
    # Try to delete non-existent workspace
    success = WorkspaceService(db).delete_workspace(uuid4())

    # Assertion
    assert success is False


def test_search_workspaces_with_filters(db: Session, setup_workspace):
    workspace = setup_workspace

    # Search using ilike filter
    filters = {"name": {"operator": "ilike", "value": f"%{workspace.name}%"}}
    results = WorkspaceService(db).search(filters)

    assert isinstance(results, list)
    assert any(result.id == workspace.id for result in results)

    # Search using exact match
    filters = {"name": workspace.name}
    results = WorkspaceService(db).search(filters)

    assert len(results) == 1
    assert results[0].id == workspace.id

    # Search with no match
    filters = {"name": {"operator": "==", "value": "Nonexistent Name"}}
    results = WorkspaceService(db).search(filters)

    assert len(results) == 0
