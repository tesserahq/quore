from app.config import get_settings
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
from llama_index.core.base.embeddings.base import BaseEmbedding
from typing import Optional
from llama_index.vector_stores.postgres import PGVectorStore
from app.core.telemetry import instrument_method
from app.core.storage_manager import StorageManager


class Ingestor:
    """A class to handle document ingestion into vector stores.

    This class manages the ingestion of documents into vector stores,
    handling both raw text and pre-processed documents. It works in
    conjunction with IndexManager to maintain vector indices.

    Args:
        embedding_model (BaseEmbedding): The embedding model to use
        vector_store (PGVectorStore): The vector store to use
        storage (StorageManager, optional): Storage manager instance. Defaults to a new StorageManager instance.
    """

    def __init__(
        self,
        embedding_model: BaseEmbedding,
        vector_store: PGVectorStore,
        storage: Optional[StorageManager] = None,
    ):
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.settings = get_settings()
        self.storage = storage or StorageManager()

    @instrument_method()
    def ingest_raw_text(
        self, ref_id: str, text: str, labels: Optional[dict[str, str]] = None
    ):
        """Ingest raw text into the vector store.

        Args:
            ref_id (str): Unique identifier for the document
            text (str): Raw text content to be ingested
            labels (Optional[dict[str, str]]): Optional metadata labels for the document
        """
        print(labels)
        # Create a document from the raw text
        document = Document(
            text=text,
            id_=ref_id,
            metadata=labels,
        )

        # create (or load) docstore and add nodes
        docstore = self.storage.get_docstore()

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
        index.update_ref_doc(document)
