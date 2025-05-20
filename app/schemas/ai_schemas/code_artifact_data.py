from pydantic import BaseModel


class CodeArtifactData(BaseModel):
    file_name: str
    code: str
    language: str
