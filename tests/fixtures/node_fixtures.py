import pytest
from app.models.node import get_node_model
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from app.core.index_manager import IndexManager


def ensure_index_table_exists(db_session, project):
    """Ensure the index table exists for the project.

    This function checks if the table exists and creates it if it doesn't.
    It also handles the case where the table might be defined multiple times
    in the SQLAlchemy metadata.
    """
    inspector = inspect(db_session.get_bind())
    table_name = project.vector_llama_index_name()

    if table_name not in inspector.get_table_names():
        index_manager = IndexManager(db_session, project)
        index_manager.create_index()


@pytest.fixture
def setup_node(db: Session, setup_project, faker):
    """Create a single node for testing."""
    project = setup_project
    ensure_index_table_exists(db, project)
    Node = get_node_model(project)

    node_data = {
        "text": faker.text(200),
        "metadata_": {"source": faker.url()},
        "node_id": faker.uuid4(),
        "embedding": [0.0] * 1536,  # Mock embedding dimension
    }

    node = Node(**node_data)
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


@pytest.fixture
def setup_nodes(db: Session, setup_project, faker, count: int = 3):
    """Create multiple nodes for testing.

    Args:
        db: Database session
        setup_project: Project fixture
        faker: Faker instance
        count: Number of nodes to create (default: 3)

    Returns:
        List of created nodes
    """
    nodes = []
    project = setup_project
    ensure_index_table_exists(db, project)
    Node = get_node_model(project)

    for _ in range(count):
        node_data = {
            "text": faker.text(200),
            "metadata_": {"source": faker.url()},
            "node_id": faker.uuid4(),
            "embedding": [0.0] * 1536,  # Mock embedding dimension
        }
        node = Node(**node_data)
        db.add(node)
        db.commit()
        db.refresh(node)
        nodes.append(node)
    return nodes
