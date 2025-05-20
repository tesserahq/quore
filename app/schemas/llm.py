from pydantic import BaseModel
from typing import List, Optional


class EmbeddingModel(BaseModel):
    """Model for embedding model information."""

    embed_model: str
    default_embed_dim: int
    available_dimensions: List[int]
    max_tokens: int
    miracl_avg: float
    mteb_avg: float
    default: Optional[bool] = None
    hnsw_m: Optional[int] = None
    hnsw_ef_search: Optional[int] = None
    hnsw_dist_method: Optional[str] = None
    hnsw_ef_construction: Optional[int] = None


class Provider(BaseModel):
    """Model for provider information."""

    name: str
    embedding_models: List[EmbeddingModel]
