from app.models.project import Project
from app.config import get_settings


def test_project_default_attributes():
    # Create a project with minimal required attributes
    project = Project(
        name="Test Project", workspace_id="00000000-0000-0000-0000-000000000000"
    )

    settings = get_settings()

    # Verify default attributes are set correctly
    assert project.llm_provider == settings.default_llm_provider
    assert project.embed_model == settings.default_embed_model
    assert project.embed_dim == settings.default_embed_dim
    assert project.llm == settings.default_llm

    # Verify ingest settings are set with defaults
    assert project.ingest_settings["data_dir"] == settings.default_data_dir
    assert project.ingest_settings["hnsw_m"] == settings.default_hnsw_m
    assert (
        project.ingest_settings["hnsw_ef_construction"]
        == settings.default_hnsw_ef_construction
    )
    assert project.ingest_settings["hnsw_ef_search"] == settings.default_hnsw_ef_search
    assert (
        project.ingest_settings["hnsw_dist_method"] == settings.default_hnsw_dist_method
    )


def test_project_custom_ingest_settings():
    # Create a project with custom ingest settings
    custom_settings = {
        "data_dir": "/custom/path",
        "hnsw_m": 32,
        "hnsw_ef_construction": 200,
        "hnsw_ef_search": 100,
        "hnsw_dist_method": "vector_cosine_ops",
    }

    project = Project(
        name="Test Project",
        workspace_id="00000000-0000-0000-0000-000000000000",
        ingest_settings=custom_settings,
    )

    # Verify custom settings are preserved
    assert project.ingest_settings["data_dir"] == "/custom/path"
    assert project.ingest_settings["hnsw_m"] == 32
    assert project.ingest_settings["hnsw_ef_construction"] == 200
    assert project.ingest_settings["hnsw_ef_search"] == 100
    assert project.ingest_settings["hnsw_dist_method"] == "vector_cosine_ops"


def test_project_custom_llm_settings():
    # Create a project with custom LLM settings
    project = Project(
        name="Test Project",
        workspace_id="00000000-0000-0000-0000-000000000000",
        llm="gpt-4",
        embed_model="text-embedding-3-large",
    )

    # Verify custom LLM settings are preserved
    assert project.llm == "gpt-4"
    assert project.embed_model == "text-embedding-3-large"
