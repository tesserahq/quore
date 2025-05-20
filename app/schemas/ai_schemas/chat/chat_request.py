from typing import Any, Optional
from pydantic import BaseModel
from app.schemas.ai_schemas.chat.chat_api_message import ChatAPIMessage
from app.schemas.ai_schemas.chat.chat_config import ChatConfig
from typing import List
from pydantic import field_validator
from llama_index.core.types import MessageRole


class ChatRequest(BaseModel):
    messages: List[ChatAPIMessage]
    data: Optional[Any] = None
    config: Optional[ChatConfig] = ChatConfig()

    @field_validator("messages")
    def validate_messages(cls, v: List[ChatAPIMessage]) -> List[ChatAPIMessage]:
        if v[-1].role != MessageRole.USER:
            raise ValueError("Last message must be from user")
        return v
