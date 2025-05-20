from typing import Literal
from pydantic import BaseModel


class DocumentArtifactData(BaseModel):
    title: str
    content: str
    type: Literal["markdown", "html"]
