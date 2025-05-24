from llama_index.storage.docstore.redis import RedisDocumentStore
from app.config import get_settings


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