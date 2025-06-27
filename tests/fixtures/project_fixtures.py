from app.constants.providers import MOCK_PROVIDER
import pytest
from app.models.project import Project
from sqlalchemy.orm import Session


@pytest.fixture
def setup_project(db: Session, setup_workspace, faker):
    """Create a test project in the database with optional overrides."""
    workspace = setup_workspace

    project_data = {
        "name": faker.company(),
        "description": faker.text(100),
        "workspace_id": workspace.id,
        "llm_provider": MOCK_PROVIDER,
        "embed_model": "mock",
        "embed_dim": 1536,
        "llm": "mock",
    }

    project = Project(**project_data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
