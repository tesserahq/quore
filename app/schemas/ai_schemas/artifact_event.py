from app.schemas.ai_schemas.artifact import Artifact
from llama_index.core.workflow import Event


class ArtifactEvent(Event):
    type: str = "artifact"
    data: Artifact

    def to_response(self) -> dict:
        return {
            "type": self.type,
            "data": self.data.model_dump(),
        }
