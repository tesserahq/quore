from llama_index.storage.docstore.redis import RedisDocumentStore
from app.config import get_settings
from app.models.project import Project
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy.orm import Session
from llama_index.core.schema import Document
from app.constants.providers import (
    OPENAI_PROVIDER,
    get_embedding_provider,
    get_llm_provider,
)
from sqlalchemy import text
from typing import Optional
from llama_index.core.indices import load_index_from_storage
from llama_index.core.tools.query_engine import QueryEngineTool
from llama_index.core.base.base_query_engine import BaseQueryEngine
from typing import Any
import os
from llama_index.llms.openai import OpenAI
from app.core.logging_config import get_logger
from llama_index.storage.chat_store.postgres import PostgresChatStore
from llama_index.core.memory import ChatMemoryBuffer

logger = get_logger()


class IndexManager:
    def __init__(self, db_session: Session, project: Project):
        self.db = db_session
        self.project = project
        self.ingest_settings = project.ingest_settings_obj()
        self.settings = get_settings()
        self.logger = get_logger()

    def get_redis_docstore(self) -> RedisDocumentStore:
        """Get a Redis document store instance using settings from config."""
        print(self.settings.redis_host)
        print(self.settings.redis_port)
        print(self.settings.redis_namespace)
        return RedisDocumentStore.from_host_and_port(
            host=self.settings.redis_host,
            port=self.settings.redis_port,
            namespace=self.settings.redis_namespace,
        )

    def get_chat_memory(self, project_id: str, user_id: str) -> PostgresChatStore:
        """Get a chat store instance using settings from config."""
        settings = get_settings()
        chat_store = PostgresChatStore.from_uri(
            uri=settings.database_url,
        )

        return ChatMemoryBuffer.from_defaults(
            token_limit=3000,
            chat_store=chat_store,
            chat_store_key=f"{project_id}-{user_id}",
        )

    def create_index(self):
        """Create an index for a given project."""

        # create (or load) docstore and add nodes
        docstore = self.get_redis_docstore()

        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store(), docstore=docstore
        )

        # TODO: I think it would be a good idea to have a default document per project
        # to ensure that the index is created even if no documents are ingested
        # This is a placeholder document. You should replace it with actual documents.
        document = Document(text="Hello world", id_=str(self.project.id))

        self.logger.debug(
            "IndexManager: Creating index", extra={"project_id": self.project.id}
        )
        index = VectorStoreIndex.from_documents(
            [document],
            storage_context=storage_context,
            embed_model=self.embedding_model(),
            show_progress=False,
        )
        return index

    def load_index(self):
        """Load an index for a given project."""

        # create (or load) docstore and add nodes
        docstore = self.get_redis_docstore()

        embed_model = self.embedding_model()

        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store(), docstore=docstore
        )

        index = VectorStoreIndex(
            [], storage_context=storage_context, embed_model=embed_model
        )

        return index

    def drop_index(self):
        # Logic to drop the index table
        table_name = self.project.vector_llama_index_name()
        self.db.execute(text(f"DROP TABLE IF EXISTS {table_name};"))
        self.db.commit()

    def vector_store(self):
        self.logger.debug(
            "IndexManager: Creating vector store", extra={"project_id": self.project.id}
        )
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

    def ingest_raw_text(
        self, id: str, text: str, labels: Optional[dict[str, str]] = None
    ):
        """Ingest raw text into the vector store for a given project."""
        # Create a document from the raw text
        document = Document(
            text=text, id_=id, metadata={"labels": labels, "ref_doc_id": id}
        )

        index = self.load_index()
        self.logger.info("Refreshing docs")
        index.refresh_ref_docs([document])
        # index.update_ref_doc(document)

        # # Create the vector store
        # self.ingest_documents([document])

    def ingest_documents(self, documents: list[Document]):
        """Ingest documents into the vector store for a given project."""
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store())
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=False,
            embed_model=self.embedding_model(),
        )

        return index

    def create_query_engine(self, **kwargs: Any) -> BaseQueryEngine:
        """
        Create a query engine for the given index.

        Args:
            index: The index to create a query engine for.
            params (optional): Additional parameters for the query engine, e.g: similarity_top_k
        """
        # TODO: This settings should come from the project settings
        top_k = int(os.getenv("TOP_K", 0))
        if top_k != 0 and kwargs.get("filters") is None:
            kwargs["similarity_top_k"] = top_k

        index = self.load_index()

        self.logger.debug(
            "IndexManager: Loading LLM", extra={"project_id": self.project.id}
        )
        llm = OpenAI(model="gpt-4o-mini", api_key=self.project_openai_api_key())

        self.logger.debug(
            "IndexManager: Creating query engine", extra={"project_id": self.project.id}
        )
        query_engine = index.as_query_engine(llm=llm)

        self.logger.debug(
            "IndexManager: Query engine created", extra={"project_id": self.project.id}
        )
        return query_engine

    def get_query_engine_tool(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> QueryEngineTool:
        """
        Get a query engine tool for the given index.

        Args:
            index: The index to create a query engine for.
            name (optional): The name of the tool.
            description (optional): The description of the tool.
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

    # def ingest(self, labels: Optional[dict[str, str]] = None):
    #     """Ingest documents into the vector store for a given project."""

    #     # load the documents and create the index
    #     reader = SimpleDirectoryReader(
    #         self.settings.data_dir,
    #         recursive=True,
    #     )

    #     documents = reader.load_data()

    #     storage_context = StorageContext.from_defaults(vector_store=self.vector_store())
    #     index = VectorStoreIndex.from_documents(
    #         documents, storage_context=storage_context, show_progress=False,
    #         metadata=labels
    #     )
    #     query_engine = index.as_query_engine()

    def embedding_model(self):
        self.logger.debug(
            "IndexManager: Getting Embedding model",
            extra={"project_id": self.project.id},
        )
        return get_embedding_provider(
            self.project.llm_provider,
            model_name=self.project.embed_model,
            api_key=self.project_openai_api_key(),
        )

    def llm(self):
        self.logger.debug(
            "IndexManager: LLM provider: %s",
            self.project.llm_provider,
            extra={"project_id": self.project.id},
        )
        return get_llm_provider(
            self.project.llm_provider,
            model_name=self.project.llm,
            api_key=self.project_openai_api_key(),
        )

    def project_openai_api_key(self):
        if self.project.llm_provider != OPENAI_PROVIDER:
            return None

        if self.ingest_settings.has_key("openai_api_key") == False:
            self.logger.debug(
                "IndexManager: Using global OpenAI API key",
                extra={"project_id": self.project.id},
            )
            return self.settings.openai_api_key

        self.logger.debug(
            "IndexManager: Using project-specific OpenAI API key",
            extra={"project_id": self.project.id},
        )
        return self.ingest_settings.get("openai_api_key")  # adapt as needed
