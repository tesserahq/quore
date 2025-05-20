from pydantic import BaseModel
from llama_index.core.types import ChatMessage, MessageRole
from typing import Optional, List, Any


class ChatAPIMessage(BaseModel):
    role: MessageRole
    content: str
    annotations: Optional[List[Any]] = None

    def to_llamaindex_message(self) -> ChatMessage:
        return ChatMessage(role=self.role, content=self.content)
