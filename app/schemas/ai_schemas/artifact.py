import logging

from typing import Optional, Union
from pydantic import BaseModel

from app.schemas.ai_schemas.artifact_type import ArtifactType
from app.schemas.ai_schemas.code_artifact_data import CodeArtifactData
from app.schemas.ai_schemas.chat.chat_api_message import ChatAPIMessage
from app.schemas.ai_schemas.document_artifact_data import DocumentArtifactData

logger = logging.getLogger("uvicorn")


class Artifact(BaseModel):
    created_at: Optional[int] = None
    type: ArtifactType
    data: Union[CodeArtifactData, DocumentArtifactData]

    @classmethod
    def from_message(cls, message: ChatAPIMessage) -> Optional["Artifact"]:
        if not message.annotations or not isinstance(message.annotations, list):
            return None

        for annotation in message.annotations:
            if isinstance(annotation, dict) and annotation.get("type") == "artifact":
                try:
                    artifact = cls.model_validate(annotation.get("data"))
                    return artifact
                except Exception as e:
                    logger.warning(
                        f"Failed to parse artifact from annotation: {annotation}. Error: {e}"
                    )

        return None
