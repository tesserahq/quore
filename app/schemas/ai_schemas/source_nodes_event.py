from llama_index.core.workflow import Event
from app.schemas.ai_schemas.source_nodes import SourceNodes
from llama_index.core.schema import NodeWithScore
from typing import List


class SourceNodesEvent(Event):
    nodes: List[NodeWithScore]

    def to_response(self) -> dict:
        return {
            "type": "sources",
            "data": {
                "nodes": [
                    SourceNodes.from_source_node(node).model_dump()
                    for node in self.nodes
                ]
            },
        }
