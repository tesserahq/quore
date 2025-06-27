from llama_index.storage.docstore.redis import RedisDocumentStore
from app.config import get_settings
from llama_index.vector_stores.postgres import PGVectorStore
from app.models.project import Project


class StorageManager:
    """A class to manage various storage components across the application.

    This class provides centralized access to different storage services
    like document stores, vector stores, and other storage-related functionality.
    It ensures consistent configuration and initialization across different
    parts of the application.
    """

    def __init__(self):
        self.settings = get_settings()

    def get_docstore(self) -> RedisDocumentStore:
        """Get a Redis document store instance using settings from config.

        Returns:
            RedisDocumentStore: Configured Redis document store instance
        """
        return RedisDocumentStore.from_host_and_port(
            host=self.settings.redis_host,
            port=self.settings.redis_port,
            namespace=self.settings.redis_namespace,
        )

    def vector_store(self, project: Project) -> PGVectorStore:
        """Create a PostgreSQL vector store instance for the project.

        Configures and returns a PGVectorStore instance with project-specific
        settings including HNSW parameters for hybrid search.

        Args:
            project (Project): Project instance containing configuration and settings

        Returns:
            PGVectorStore: Configured PostgreSQL vector store instance
        """
        ingest_settings = project.ingest_settings_obj()
        return PGVectorStore.from_params(
            database=self.settings.database_url_obj.database,
            host=self.settings.database_url_obj.host,
            password=self.settings.database_url_obj.password,
            port=self.settings.database_url_obj.port,
            user=self.settings.database_url_obj.username,
            table_name=project.vector_index_name(),
            embed_dim=project.embed_dim,
            hybrid_search=True,
            hnsw_kwargs={
                "hnsw_m": ingest_settings.hnsw_m,
                "hnsw_ef_construction": ingest_settings.hnsw_ef_construction,
                "hnsw_ef_search": ingest_settings.hnsw_ef_search,
                "hnsw_dist_method": ingest_settings.hnsw_dist_method,
            },
        )
