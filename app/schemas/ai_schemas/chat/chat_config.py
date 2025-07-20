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
