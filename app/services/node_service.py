from __future__ import annotations

from typing import Any, Dict, Optional, List
import json

from app.schemas.project import NodeResponse
from app.models.project import Project
from app.models.node import get_node_model
from sqlalchemy.orm import Session


class NodeService:
    """Service for transforming Node ORM objects into API-ready responses."""

    def __init__(self, db: Session):
        self.db = db

    def get_nodes(self, project: Project) -> List[Any]:
        """Return all nodes for a given project using the dynamic Node model."""
        Node = get_node_model(project)
        return self.db.query(Node).all()

    @staticmethod
    def build_node_response(node: Any) -> NodeResponse:
        """Build a NodeResponse from a Node ORM instance.

        This extracts labels and doc_id from the node's metadata, and falls back to parsing
        the serialized `_node_content` when present.
        """
        node_dict = node.__dict__.copy()

        # Normalize metadata
        raw_metadata = node_dict.get("metadata_")
        if not isinstance(raw_metadata, dict):
            metadata: Optional[Dict[str, Any]] = None
        else:
            metadata = raw_metadata

        # Extract labels and doc_id
        labels: Optional[Dict[str, Any]] = None
        doc_id: Optional[str] = None

        if metadata:
            # Labels from top-level metadata
            labels_value = metadata.get("labels")
            if isinstance(labels_value, dict):
                labels = labels_value

            # doc_id from common keys
            for key in ("doc_id", "document_id", "ref_doc_id"):
                value = metadata.get(key)
                if isinstance(value, str) and value:
                    doc_id = value
                    break

            # Fallback: parse _node_content JSON string if present
            if (labels is None or doc_id is None) and isinstance(
                metadata.get("_node_content"), str
            ):
                try:
                    inner = json.loads(metadata["_node_content"])  # type: ignore[index]
                    if labels is None:
                        inner_metadata = inner.get("metadata")
                        if isinstance(inner_metadata, dict):
                            inner_labels = inner_metadata.get("labels")
                            if isinstance(inner_labels, dict):
                                labels = inner_labels
                    if doc_id is None:
                        for key in ("doc_id", "document_id", "ref_doc_id"):
                            value = inner.get(key)
                            if isinstance(value, str) and value:
                                doc_id = value
                                break
                except Exception:
                    # Ignore parsing issues; keep labels/doc_id as None
                    pass

        response_payload = {
            "id": node_dict.get("id"),
            "text": node_dict.get("text"),
            "node_id": node_dict.get("node_id"),
            "doc_id": doc_id,
            "labels": labels,
        }

        return NodeResponse.model_validate(response_payload)
