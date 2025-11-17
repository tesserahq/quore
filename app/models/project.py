from typing import Any
from app.models.mixins import TimestampMixin, SoftDeleteMixin
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_json import mutable_json_type  # type: ignore
from sqlalchemy.dialects.postgresql import JSONB
from app.config import get_settings

import uuid

from app.db import Base


class RAGSettings:
    __slots__ = ("_data",)

    _schema = {
        "similarity_top_k": int,
        "text_qa_template": str,
        "refine_template": str,
        "response_mode": str,
    }

    _allowed_keys = set(_schema.keys())

    def __init__(self, data=None, settings=None):
        self._data = {}
        settings = settings or get_settings()
        data = data or {}

        for key in self._allowed_keys:
            raw_value = data.get(key, getattr(settings, f"default_{key}", None))
            if raw_value is None:
                continue
            self._data[key] = self._coerce_type(key, raw_value)

    def __getattr__(self, name):
        if name not in self._allowed_keys:
            raise AttributeError(f"No such attribute: {name}")
        return self._data.get(name)

    def __setattr__(self, name, value):
        if name == "_data":
            super().__setattr__(name, value)
        elif name not in self._allowed_keys:
            raise AttributeError(f"Invalid attribute: {name}")
        else:
            self._data[name] = self._coerce_type(name, value)

    def _coerce_type(self, key, value):
        expected_type = self._schema[key]
        if not isinstance(value, expected_type):
            try:
                return expected_type(value)
            except (ValueError, TypeError):
                raise ValueError(
                    f"Invalid type for '{key}': expected {expected_type.__name__}, got {type(value).__name__}"
                )
        return value

    def to_dict(self):
        return self._data.copy()


class IngestSettings:
    __slots__ = ("_data",)

    # Map keys to their expected types
    _schema = {
        "data_dir": str,
        "hnsw_m": int,
        "hnsw_ef_construction": int,
        "hnsw_ef_search": int,
        "hnsw_dist_method": str,
    }

    _allowed_keys = set(_schema.keys())

    def __init__(self, data=None, settings=None):
        self._data = {}
        settings = settings or get_settings()
        data = data or {}

        for key in self._allowed_keys:
            raw_value = data.get(key, getattr(settings, f"default_{key}", None))
            if raw_value is None:
                raise ValueError(f"Missing required ingest setting for key: '{key}'")
            self._data[key] = self._coerce_type(key, raw_value)

    def __getattr__(self, name):
        if name not in self._allowed_keys:
            raise AttributeError(f"No such attribute: {name}")
        return self._data.get(name)

    def __setattr__(self, name, value):
        if name == "_data":
            super().__setattr__(name, value)
        elif name not in self._allowed_keys:
            raise AttributeError(f"Invalid attribute: {name}")
        else:
            self._data[name] = self._coerce_type(name, value)

    def has_key(self, key: str) -> bool:
        return key in self._allowed_keys

    def _coerce_type(self, key, value):
        expected_type = self._schema[key]
        if not isinstance(value, expected_type):
            try:
                return expected_type(value)
            except (ValueError, TypeError):
                raise ValueError(
                    f"Invalid type for '{key}': expected {expected_type.__name__}, got {type(value).__name__}"
                )
        return value

    def to_dict(self):
        return self._data.copy()


class Project(Base, TimestampMixin, SoftDeleteMixin):
    """Project model for the application."""

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    description = Column(String, nullable=True)
    logo = Column(String, nullable=True)  # We'll handle file uploads separately
    llm_provider = Column(String, nullable=False)
    embed_model = Column(String, nullable=False)
    embed_dim = Column(Integer, nullable=False)
    system_prompt = Column(String, nullable=True)
    llm = Column(String, nullable=False)
    labels = Column(JSONB, default=dict, nullable=False)  # Dictionary of labels
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    ingest_settings: Column[dict] = Column(
        mutable_json_type(dbtype=JSONB, nested=True), default=dict
    )
    rag_settings = Column[dict](
        mutable_json_type(dbtype=JSONB, nested=True), default=dict, nullable=False
    )

    def rag_settings_obj(self) -> RAGSettings:
        return RAGSettings(self.rag_settings or {}, settings=get_settings())

    def ingest_settings_obj(self) -> IngestSettings:
        return IngestSettings(self.ingest_settings or {}, settings=get_settings())

    def vector_index_name(self):
        """Return the vector index name for the project."""
        return f"{str(self.id).replace('-', '_')}_index"

    def vector_llama_index_name(self):
        """Return the full vector index name for the project.
        LlamaIndex adds a prefix to the index name."""
        return f"data_{self.vector_index_name()}"

    # Relationships
    workspace = relationship("Workspace", back_populates="projects")
    plugins = relationship("ProjectPlugin", back_populates="project")
    memberships = relationship(
        "ProjectMembership", back_populates="project", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        ingest_data = kwargs.pop("ingest_settings", None)
        settings = get_settings()

        default_ingest = {
            "data_dir": settings.default_data_dir,
            "hnsw_m": settings.default_hnsw_m,
            "hnsw_ef_construction": settings.default_hnsw_ef_construction,
            "hnsw_ef_search": settings.default_hnsw_ef_search,
            "hnsw_dist_method": settings.default_hnsw_dist_method,
        }

        if ingest_data is None:
            ingest_data = default_ingest
        else:
            # merge defaults with override values
            ingest_data = {**default_ingest, **ingest_data}

        kwargs.setdefault("ingest_settings", ingest_data)
        kwargs.setdefault("llm_provider", settings.default_llm_provider)
        kwargs.setdefault("embed_model", settings.default_embed_model)
        kwargs.setdefault("embed_dim", settings.default_embed_dim)
        kwargs.setdefault("llm", settings.default_llm)
        super().__init__(**kwargs)
