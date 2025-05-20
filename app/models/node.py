from typing import Optional, Dict, Any, List
from sqlalchemy import Column, BigInteger, String, JSON
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from pgvector.sqlalchemy import Vector
from app.db import Base
from app.models.project import Project


def get_node_model(project: Project):
    """Factory function to create a Node model with the correct table name for a project."""

    class Node(Base):
        """Node model for storing vector index data."""

        __tablename__ = project.vector_llama_index_name()
        __table_args__ = {"extend_existing": True}  # Allow table redefinition

        id = Column(BigInteger, primary_key=True, autoincrement=True)
        text = Column(String, nullable=False)
        metadata_ = Column(JSON, nullable=True)
        node_id = Column(String, nullable=True)
        embedding: Column[Optional[List[float]]] = Column(
            Vector(1536), nullable=True
        )  # Using pgvector's Vector type with 1536 dimensions
        text_search_tsv = Column(
            TSVECTOR,
            nullable=True,
            server_default="generated always as (to_tsvector('english'::regconfig, text::text)) stored",
        )

        def __repr__(self):
            return f"<Node(id={self.id}, node_id={self.node_id})>"

    return Node
