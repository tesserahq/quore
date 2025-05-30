from app.core.index_manager import IndexManager
from llama_index.core import VectorStoreIndex
from sqlalchemy import inspect


def test_index_manager_initialization(db, setup_project):
    """Test that IndexManager initializes correctly with a project."""
    project = setup_project
    index_manager = IndexManager(db, project)

    assert index_manager.project == project
    assert index_manager.db == db
    assert (
        index_manager.ingest_settings.data_dir == project.ingest_settings_obj().data_dir
    )
    assert (
        index_manager.ingest_settings.embed_dim
        == project.ingest_settings_obj().embed_dim
    )
    assert index_manager.ingest_settings.hnsw_m == project.ingest_settings_obj().hnsw_m
    assert (
        index_manager.ingest_settings.hnsw_ef_construction
        == project.ingest_settings_obj().hnsw_ef_construction
    )
    assert (
        index_manager.ingest_settings.hnsw_ef_search
        == project.ingest_settings_obj().hnsw_ef_search
    )
    assert (
        index_manager.ingest_settings.hnsw_dist_method
        == project.ingest_settings_obj().hnsw_dist_method
    )
    assert index_manager.ingestor is not None


def test_create_index(db, setup_project):
    """Test creating a new index."""
    project = setup_project
    index_manager = IndexManager(db, project)

    # Create the index
    index = index_manager.create_index()

    # Verify the index was created
    assert isinstance(index, VectorStoreIndex)

    # Verify the table exists in the database
    inspector = inspect(db.get_bind())
    assert inspector.has_table(project.vector_llama_index_name())


def test_load_index(db, setup_project):
    """Test loading an existing index."""
    project = setup_project
    index_manager = IndexManager(db, project)

    # First create the index
    index_manager.create_index()

    # Then load it
    index = index_manager.load_index()

    # Verify we got a valid index
    assert isinstance(index, VectorStoreIndex)


def test_drop_index(db, setup_project):
    """Test dropping an index."""
    project = setup_project
    index_manager = IndexManager(db, project)

    # First create the index
    index_manager.create_index()

    # Verify the table exists
    inspector = inspect(db.get_bind())
    assert inspector.has_table(project.vector_llama_index_name())

    # Drop the index
    index_manager.drop_index()

    # Re-instantiate inspector to avoid caching
    inspector = inspect(db.get_bind())
    # Verify the table no longer exists
    assert not inspector.has_table(project.vector_llama_index_name())


def test_create_query_engine(db, setup_project):
    """Test creating a query engine."""
    project = setup_project
    index_manager = IndexManager(db, project)

    # Create the index first
    index_manager.create_index()

    # Create the query engine
    query_engine = index_manager.create_query_engine()

    # Verify we got a valid query engine
    assert query_engine is not None
    assert hasattr(query_engine, "query")


def test_get_query_engine_tool(db, setup_project):
    """Test getting a query engine tool."""
    project = setup_project
    index_manager = IndexManager(db, project)

    # Create the index first
    index_manager.create_index()

    # Get the query engine tool
    tool = index_manager.get_query_engine_tool()

    # Verify we got a valid tool
    assert tool is not None


def test_embedding_model(db, setup_project):
    """Test getting the embedding model."""
    project = setup_project
    index_manager = IndexManager(db, project)

    # Get the embedding model
    embed_model = index_manager.embedding_model()

    # Verify we got a valid embedding model
    assert embed_model is not None
    assert hasattr(embed_model, "get_text_embedding")


def test_llm(db, setup_project):
    """Test getting the LLM."""
    project = setup_project
    index_manager = IndexManager(db, project)

    # Get the LLM
    llm = index_manager.llm()

    # Verify we got a valid LLM
    assert llm is not None
    assert hasattr(llm, "complete")


# def test_llm_api_key_with_project_key(db, setup_project):
#     """Test getting the LLM API key when project has its own key."""
#     project = setup_project
#     project.llm_provider = "openai"  # Ensure we're using OpenAI provider
#     # Set the key directly in the ingest_settings dict
#     project.ingest_settings["openai_api_key"] = "project-specific-key"
#     db.commit()

#     index_manager = IndexManager(db, project)
#     api_key = index_manager.llm_api_key()

#     assert api_key == "project-specific-key"


def test_llm_api_key_without_project_key(db, setup_project):
    """Test getting the LLM API key when project has no key."""
    project = setup_project
    project.llm_provider = "openai"  # Ensure we're using OpenAI provider
    project.ingest_settings = {
        "data_dir": project.ingest_settings.get("data_dir", ""),
        "embed_dim": project.ingest_settings.get("embed_dim", 1536),
        "hnsw_m": project.ingest_settings.get("hnsw_m", 16),
        "hnsw_ef_construction": project.ingest_settings.get(
            "hnsw_ef_construction", 200
        ),
        "hnsw_ef_search": project.ingest_settings.get("hnsw_ef_search", 100),
        "hnsw_dist_method": project.ingest_settings.get("hnsw_dist_method", "cosine"),
    }
    db.commit()

    index_manager = IndexManager(db, project)
    api_key = index_manager.llm_api_key()

    # Should return the default API key from settings
    assert api_key is not None
