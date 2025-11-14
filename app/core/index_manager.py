from app.config import get_settings
from app.core.ingestor import Ingestor
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
from app.core.logging_config import get_logger
from llama_index.storage.chat_store.postgres import PostgresChatStore
from llama_index.core.memory import ChatMemoryBuffer
from app.core.telemetry import instrument_method, instrument_span
from app.core.storage_manager import StorageManager


class IndexManager:
    """A class to manage vector indices and document storage for projects.

    This class handles the creation, loading, and management of vector indices
    using LlamaIndex, with support for Redis document storage and PostgreSQL
    vector storage. It provides functionality for document querying,
    and chat memory management.

    Args:
        db_session (Session): SQLAlchemy database session
        project (Project): Project instance containing configuration and settings
        storage (StorageManager, optional): Storage manager instance. Defaults to a new StorageManager instance.
    """

    def __init__(
        self,
        db_session: Session,
        project: Project,
        storage: Optional[StorageManager] = None,
    ):
        self.db = db_session
        self.project = project
        self.ingest_settings = project.ingest_settings_obj()
        self.settings = get_settings()
        self.logger = get_logger()
        self.storage = storage or StorageManager()
        self.ingestor = Ingestor(
            embedding_model=self.embedding_model(),
            vector_store=self.storage.vector_store(self.project),
            storage=self.storage,
        )

    def get_chat_memory(self, session_id: str) -> ChatMemoryBuffer:
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
            chat_store_key=session_id,
        )

    def default_text(self) -> str:
        """Get the default text content for initializing a new index.

        Returns:
            str: The content of the default markdown file
        """
        default_doc_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "assets",
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

        docstore = self.storage.get_docstore()

        with instrument_span("create_storage_context") as storage_span:
            storage_context = StorageContext.from_defaults(
                vector_store=self.storage.vector_store(self.project), docstore=docstore
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
        docstore = self.storage.get_docstore()

        embed_model = self.ingestor.embedding_model

        storage_context = StorageContext.from_defaults(
            vector_store=self.storage.vector_store(self.project), docstore=docstore
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

    @instrument_method()
    def reset_index(self):
        """Delete all rows from the project's vector index table without dropping it."""
        table_name = self.project.vector_llama_index_name()
        self.db.execute(text(f"DELETE FROM {table_name};"))
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

        query_engine = index.as_query_engine(llm=self.llm(), **kwargs)

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

        query_engine = self.create_query_engine(**kwargs)

        return QueryEngineTool.from_defaults(
            query_engine=query_engine,
            name=name,
            description=description,
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
            base_url=self.settings.ollama_base_url,
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

        if not self.ingest_settings.has_key("openai_api_key"):
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
