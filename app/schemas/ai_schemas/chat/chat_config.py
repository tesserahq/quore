from typing import Optional
from pydantic import BaseModel, Field


class ChatConfig(BaseModel):
    next_question_suggestions: bool = Field(
        default=True,
        description="Whether to suggest next questions",
    )
    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode for tool execution and detailed logging",
    )
    system_prompt_id: Optional[str] = Field(
        default=None,
        description="The ID of the system prompt to use",
    )
