from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, cast, List, Union
from uuid import UUID
from datetime import datetime
from typing import Literal
from app.constants.providers import LLMProviderType, OPENAI_PROVIDER
from app.config import get_settings


class IngestSettings(BaseModel):
    data_dir: str = Field(..., description="Directory path for data storage.")
    embed_dim: int = Field(..., description="Dimension of the embedding vectors.")
    hnsw_m: int = Field(
        ...,
        description="HNSW graph M parameter for approximate nearest neighbor search.",
    )
    hnsw_ef_construction: int = Field(
        ..., description="HNSW index construction quality parameter."
    )
    hnsw_ef_search: int = Field(..., description="HNSW search quality parameter.")
    hnsw_dist_method: str = Field(
        ..., description="Distance method for HNSW index (e.g. 'cosine')."
    )
    openai_api_key: Optional[str] = Field(
        None, description="Project-specific OpenAI API key if using OpenAI provider."
    )


class ProjectBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="The name of the project. Must be between 1 and 100 characters.",
    )
    description: Optional[str] = Field(
        None, description="Optional description of the project and its purpose."
    )
    workspace_id: Optional[UUID] = Field(
        None, description="The UUID of the workspace this project belongs to."
    )
    ingest_settings: Optional[IngestSettings] = Field(
        None,
        description="Optional configuration for data ingestion settings and parameters.",
    )
    llm_provider: LLMProviderType = Field(
        default=cast(LLMProviderType, OPENAI_PROVIDER),
        description="The LLM provider to use for this project. Defaults to OpenAI.",
    )
    embed_model: str = Field(
        default_factory=lambda: get_settings().default_embed_model,
        description="The embedding model to use for vector embeddings. Defaults to the system's default embedding model.",
    )
    llm: str = Field(
        default_factory=lambda: get_settings().default_llm,
        description="The specific LLM model to use for this project. Defaults to the system's default LLM.",
    )


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    ingest_settings: Optional[Dict[str, Any]] = None


class ProjectInDB(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Project(ProjectInDB):
    pass


class SearchOperator(BaseModel):
    operator: Literal["=", "!=", ">", "<", ">=", "<=", "ilike", "in", "not in"] = Field(
        ...,
        description="The comparison operator to use in the search filter. Supports equality, inequality, comparison, pattern matching, and list operations.",
    )
    value: Any = Field(
        ..., description="The value to compare against using the specified operator."
    )


class ProjectSearchFilters(BaseModel):
    name: Optional[Union[str, SearchOperator]] = Field(
        None,
        description="Filter by project name. Can be a direct string match or a SearchOperator for more complex comparisons.",
    )
    description: Optional[Union[str, SearchOperator]] = Field(
        None,
        description="Filter by project description. Can be a direct string match or a SearchOperator for more complex comparisons.",
    )
    workspace_id: Optional[Union[UUID, SearchOperator]] = Field(
        None,
        description="Filter by workspace UUID. Can be a direct UUID match or a SearchOperator for more complex comparisons.",
    )
    llm_provider: Optional[Union[LLMProviderType, SearchOperator]] = Field(
        None,
        description="Filter by LLM provider type. Can be a direct provider match or a SearchOperator for more complex comparisons.",
    )
    embed_model: Optional[Union[str, SearchOperator]] = Field(
        None,
        description="Filter by embedding model. Can be a direct string match or a SearchOperator for more complex comparisons.",
    )
    llm: Optional[Union[str, SearchOperator]] = Field(
        None,
        description="Filter by LLM model. Can be a direct string match or a SearchOperator for more complex comparisons.",
    )


class ProjectSearchResponse(BaseModel):
    data: List[Project] = Field(
        ..., description="List of projects matching the search criteria."
    )


class NodeResponse(BaseModel):
    id: int = Field(..., description="The unique identifier of the node")
    text: str = Field(..., description="The text content of the node")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata associated with the node"
    )
    node_id: Optional[str] = Field(
        None, description="Optional external node identifier"
    )

    class Config:
        from_attributes = True


class NodeListResponse(BaseModel):
    data: List[NodeResponse] = Field(..., description="List of nodes in the project")
