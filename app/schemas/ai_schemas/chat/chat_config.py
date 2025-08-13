from typing import Optional, Union
from uuid import UUID
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
    system_prompt_id: Optional[Union[UUID, str]] = Field(
        default=None,
        description="The ID of the system prompt to use. Can be either UUID or string prompt_id.",
    )
    initial_state: Optional[dict] = Field(
        default=None,
        description="Initial state for the workflow",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="The ID of the session",
    )
