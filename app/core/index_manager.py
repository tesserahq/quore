from llama_index.storage.docstore.redis import RedisDocumentStore
from app.config import get_settings
from app.models.project import Project
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from sqlalchemy.orm import Session
from llama_index.core.schema import Document
from app.constants.providers import (
    OPENAI_PROVIDER,
    get_llm_provider,
    get_embedding_provider,
)
from sqlalchemy import text
from typing import Optional
from llama_index.core.tools.query_engine import QueryEngineTool
from llama_index.core.base.base_query_engine import BaseQueryEngine
from typing import Any
import os
from llama_index.llms.openai import OpenAI
from app.core.logging_config import get_logger
from llama_index.storage.chat_store.postgres import PostgresChatStore
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.vector_stores.postgres import PGVectorStore
from app.core.telemetry import instrument_method, instrument_span


class IndexManager:
    """A class to manage vector indices and document storage for projects.

    This class handles the creation, loading, and management of vector indices
    using LlamaIndex, with support for Redis document storage and PostgreSQL
    vector storage. It provides functionality for document querying,
    and chat memory management.

    Args:
        db_session (Session): SQLAlchemy database session
        project (Project): Project instance containing configuration and settings
    """

    def __init__(self, db_session: Session, project: Project):
        self.db = db_session
        self.project = project
        self.ingest_settings = project.ingest_settings_obj()
        self.settings = get_settings()
        self.logger = get_logger()

    def get_redis_docstore(self) -> RedisDocumentStore:
        """Get a Redis document store instance using settings from config.

        Returns:
            RedisDocumentStore: Configured Redis document store instance
        """
        return RedisDocumentStore.from_host_and_port(
            host=self.settings.redis_host,
            port=self.settings.redis_port,
            namespace=self.settings.redis_namespace,
        )

    def get_chat_memory(self, project_id: str, user_id: str) -> ChatMemoryBuffer:
        """Get a chat memory buffer instance for a specific project and user.

        Args:
            project_id (str): Unique identifier for the project
            user_id (str): Unique identifier for the user

        Returns:
            ChatMemoryBuffer: Configured chat memory buffer with PostgreSQL storage
        """
        settings = get_settings()
        chat_store = PostgresChatStore.from_uri(
            uri=settings.database_url,
        )

        return ChatMemoryBuffer.from_defaults(
            token_limit=3000,
            chat_store=chat_store,
            chat_store_key=f"{project_id}-{user_id}",
        )

    def default_text(self) -> str:
        """Get the default text content for initializing a new index.

        Returns:
            str: The content of the default markdown file
        """
        default_doc_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "docs",
            "default_index.md",
        )
        with open(default_doc_path, "r") as f:
            return f.read()

    @instrument_method()
    def create_index(self):
        """Create a new vector index for the project.

        Creates a new vector index with a default markdown document to ensure
        the index is initialized properly. The index uses the configured
        vector store and embedding model.

        Returns:
            VectorStoreIndex: The newly created vector index
        """
        # create (or load) docstore and add nodes
        with instrument_span("get_redis_docstore") as docstore_span:
            docstore = self.get_redis_docstore()
            docstore_span.set_attribute("redis_host", self.settings.redis_host)
            docstore_span.set_attribute("redis_port", self.settings.redis_port)

        with instrument_span("create_storage_context") as storage_span:
            storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store(), docstore=docstore
            )
            storage_span.set_attribute("vector_store_type", "PGVectorStore")

        with instrument_span("create_document") as doc_span:
            document = Document(text=self.default_text(), id_=str(self.project.id))
            doc_span.set_attribute("document_id", str(self.project.id))

        with instrument_span("create_vector_store_index") as index_span:
            index = VectorStoreIndex.from_documents(
                [document],
                storage_context=storage_context,
                embed_model=self.embedding_model(),
                show_progress=False,
            )
            index_span.set_attribute("embed_model", self.project.embed_model)

        return index

    @instrument_method()
    def load_index(self):
        """Load an existing vector index for the project.

        Loads the vector index using the configured vector store and
        embedding model. If no index exists, creates an empty one.

        Returns:
            VectorStoreIndex: The loaded vector index
        """

        # create (or load) docstore and add nodes
        docstore = self.get_redis_docstore()

        embed_model = self.ingestor.embedding_model()

        storage_context = StorageContext.from_defaults(
            vector_store=self.ingestor.vector_store(), docstore=docstore
        )

        index = VectorStoreIndex(
            [], storage_context=storage_context, embed_model=embed_model
        )

        return index

    @instrument_method()
    def drop_index(self):
        """Drop the vector index table for the project.

        Removes the vector index table from the database if it exists.
        This is a destructive operation that will remove all indexed data.
        """
        # Logic to drop the index table
        table_name = self.project.vector_llama_index_name()
        self.db.execute(text(f"DROP TABLE IF EXISTS {table_name};"))
        self.db.commit()

    def create_query_engine(self, **kwargs: Any) -> BaseQueryEngine:
        """Create a query engine for the project's index.

        Creates a query engine with the project's configured LLM and
        optional parameters for query customization.

        Args:
            **kwargs: Additional parameters for the query engine configuration

        Returns:
            BaseQueryEngine: Configured query engine instance
        """
        # TODO: This settings should come from the project settings
        top_k = int(os.getenv("TOP_K", 0))
        if top_k != 0 and kwargs.get("filters") is None:
            kwargs["similarity_top_k"] = top_k

        index = self.load_index()

        llm = OpenAI(model="gpt-4o-mini", api_key=self.llm_api_key())

        query_engine = index.as_query_engine(llm=llm)

        return query_engine

    def get_query_engine_tool(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> QueryEngineTool:
        """Create a query engine tool for the project's index.

        Args:
            name (Optional[str]): Name for the query tool
            description (Optional[str]): Description of the tool's functionality
            **kwargs: Additional parameters for the query engine configuration

        Returns:
            QueryEngineTool: Configured query engine tool instance
        """
        if name is None:
            name = "query_index"
        if description is None:
            description = "Use this tool to retrieve information about the text corpus from an index."

        self.logger.debug(
            "Creating query engine", extra={"project_id": self.project.id}
        )
        query_engine = self.create_query_engine(**kwargs)
        self.logger.debug("Query engine created", extra={"project_id": self.project.id})

        self.logger.debug(
            "Creating Query engine tool", extra={"project_id": self.project.id}
        )
        return QueryEngineTool.from_defaults(
            query_engine=query_engine,
            name=name,
            description=description,
        )

    def vector_store(self) -> PGVectorStore:
        """Create a PostgreSQL vector store instance for the project.

        Configures and returns a PGVectorStore instance with project-specific
        settings including HNSW parameters for hybrid search.

        Returns:
            PGVectorStore: Configured PostgreSQL vector store instance
        """
        return PGVectorStore.from_params(
            database=self.settings.database_url_obj.database,
            host=self.settings.database_url_obj.host,
            password=self.settings.database_url_obj.password,
            port=self.settings.database_url_obj.port,
            user=self.settings.database_url_obj.username,
            table_name=self.project.vector_index_name(),
            embed_dim=self.ingest_settings.embed_dim,
            hybrid_search=True,
            hnsw_kwargs={
                "hnsw_m": self.ingest_settings.hnsw_m,
                "hnsw_ef_construction": self.ingest_settings.hnsw_ef_construction,
                "hnsw_ef_search": self.ingest_settings.hnsw_ef_search,
                "hnsw_dist_method": self.ingest_settings.hnsw_dist_method,
            },
        )

    def llm(self):
        """Get the configured LLM provider for the project.

        Returns:
            BaseLLM: Configured language model instance
        """

        return get_llm_provider(
            self.project.llm_provider,
            model_name=self.project.llm,
            api_key=self.llm_api_key(),
        )

    def llm_api_key(self):
        """Get the appropriate OpenAI API key for the project.

        Returns the project-specific API key if configured, otherwise
        falls back to the global API key.

        Returns:
            Optional[str]: OpenAI API key or None if not using OpenAI
        """
        if self.project.llm_provider != OPENAI_PROVIDER:
            return None

        if self.ingest_settings.has_key("openai_api_key") == False:
            return self.settings.openai_api_key

        return self.ingest_settings.get("openai_api_key")

    def embedding_model(self):
        """Get the configured embedding model for the project.

        Returns:
            BaseEmbedding: Configured embedding model instance
        """
        return get_embedding_provider(
            self.project.llm_provider,
            model_name=self.project.embed_model,
            api_key=self.llm_api_key(),
        )
