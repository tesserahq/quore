from app.config import get_settings
from app.constants.providers import MOCK_PROVIDER
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate


def test_create_project(db: Session, setup_workspace):
    workspace = setup_workspace
    service = ProjectService(db)
    settings = get_settings()

    project_in = ProjectCreate(
        name="Test Project",
        workspace_id=workspace.id,
        description="My first project",
        llm_provider=MOCK_PROVIDER,
        embed_model="mock",
        embed_dim=1536,
        llm="mock",
    )

    project = service.create_project(project_in)

    assert project.id is not None
    assert project.name == "Test Project"
    assert project.workspace_id == workspace.id
    assert project.description == "My first project"
    assert project.ingest_settings is not None
    assert project.llm_provider == MOCK_PROVIDER
    assert project.embed_model == "mock"
    assert project.embed_dim == 1536
    assert project.llm == "mock"

    ingest_settings_obj = project.ingest_settings_obj()
    assert ingest_settings_obj.data_dir == settings.default_data_dir
    assert ingest_settings_obj.hnsw_m == settings.default_hnsw_m
    assert (
        ingest_settings_obj.hnsw_ef_construction
        == settings.default_hnsw_ef_construction
    )
    assert ingest_settings_obj.hnsw_ef_search == settings.default_hnsw_ef_search
    assert ingest_settings_obj.hnsw_dist_method == settings.default_hnsw_dist_method

    inspector = inspect(db.get_bind())
    assert inspector.has_table(project.vector_llama_index_name())


def test_get_project(db: Session, setup_project):
    service = ProjectService(db)
    project = setup_project

    retrieved_project = service.get_project(project.id)
    assert retrieved_project.id == project.id
    assert retrieved_project.name == project.name


def test_update_project(db: Session, setup_project):
    service = ProjectService(db)
    project = setup_project

    updated = service.update_project(project.id, ProjectUpdate(name="After"))

    assert updated.name == "After"


def test_delete_project(db: Session, setup_project):
    service = ProjectService(db)
    project = setup_project

    service.delete_project(project.id)

    result = service.get_project(project.id)
    assert result is None

    inspector = inspect(db.get_bind())
    assert not inspector.has_table(project.vector_llama_index_name())


def test_search_projects_exact_match(db: Session, setup_project):
    """Test searching projects with exact matches."""
    service = ProjectService(db)
    project = setup_project

    # Test exact name match
    results = service.search({"name": project.name})
    assert len(results) == 1
    assert results[0].id == project.id

    # Test exact workspace_id match
    results = service.search({"workspace_id": project.workspace_id})
    assert len(results) == 1
    assert results[0].id == project.id

    # Test exact llm_provider match
    results = service.search({"llm_provider": project.llm_provider})
    assert len(results) == 1
    assert results[0].id == project.id


def test_search_projects_partial_match(db: Session, setup_project):
    """Test searching projects with partial matches using ilike."""
    service = ProjectService(db)
    project = setup_project

    # Test partial name match
    partial_name = project.name[: len(project.name) // 2]
    results = service.search(
        {"name": {"operator": "ilike", "value": f"%{partial_name}%"}}
    )
    assert len(results) == 1
    assert results[0].id == project.id


def test_search_projects_multiple_conditions(db: Session, setup_project):
    """Test searching projects with multiple conditions."""
    service = ProjectService(db)
    project = setup_project

    # Test multiple conditions
    results = service.search(
        {
            "name": {"operator": "ilike", "value": f"%{project.name}%"},
            "workspace_id": project.workspace_id,
            "llm_provider": project.llm_provider,
        }
    )
    assert len(results) == 1
    assert results[0].id == project.id


def test_search_projects_no_matches(db: Session):
    """Test searching projects with no matching results."""
    service = ProjectService(db)

    # Test non-existent name
    results = service.search({"name": "NonExistentProjectName123"})
    assert len(results) == 0

    # Test non-existent workspace_id
    results = service.search({"workspace_id": uuid4()})
    assert len(results) == 0


def test_search_projects_case_insensitive(db: Session, setup_project):
    """Test searching projects with case-insensitive matches."""
    service = ProjectService(db)
    project = setup_project

    # Test case-insensitive name match
    results = service.search(
        {"name": {"operator": "ilike", "value": project.name.upper()}}
    )
    assert len(results) == 1
    assert results[0].id == project.id
