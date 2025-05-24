from llama_index.storage.docstore.redis import RedisDocumentStore
from app.config import get_settings
from app.models.project import Project
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from sqlalchemy.orm import Session
from llama_index.core.schema import Document
from llama_index.core.base.embeddings.base import BaseEmbedding
from typing import Optional
from llama_index.vector_stores.postgres import PGVectorStore
from app.core.telemetry import instrument_method, instrument_span


class Ingestor:
    """A class to handle document ingestion into vector stores.

    This class manages the ingestion of documents into vector stores,
    handling both raw text and pre-processed documents. It works in
    conjunction with IndexManager to maintain vector indices.

    Args:
        db_session (Session): SQLAlchemy database session
        project (Project): Project instance containing configuration and settings
        index_manager (IndexManager): The index manager instance to use for index operations
    """

    def __init__(self, embedding_model: BaseEmbedding, vector_store: PGVectorStore):
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.settings = get_settings()

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

    @instrument_method()
    def ingest_raw_text(
        self, id: str, text: str, labels: Optional[dict[str, str]] = None
    ):
        """Ingest raw text into the vector store.

        Args:
            id (str): Unique identifier for the document
            text (str): Raw text content to be ingested
            labels (Optional[dict[str, str]]): Optional metadata labels for the document
        """
        # Create a document from the raw text
        document = Document(
            text=text,
            id_=id,
            metadata={
                "labels": labels,
            },
        )

        # create (or load) docstore and add nodes
        docstore = self.get_redis_docstore()

        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store, docstore=docstore
        )
        index = VectorStoreIndex(
            [],
            storage_context=storage_context,
            embed_model=self.embedding_model,
            show_progress=False,
        )
        # TODO: Make sure this is the correct way to update the document
        # The update method will delete the document and insert a new one
        index.update(document)
