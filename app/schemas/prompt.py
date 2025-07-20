from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class PromptBase(BaseModel):
    """Base prompt model containing common prompt attributes."""

    name: str = Field(..., min_length=1, max_length=100)
    """Name of the prompt. Must be between 1 and 100 characters."""

    prompt_id: str = Field(..., min_length=1, max_length=100)
    """Unique identifier for the prompt within the system."""

    type: str = Field(..., min_length=1, max_length=50)
    """Type/category of the prompt."""

    prompt: str = Field(..., min_length=1)
    """The actual prompt content."""

    created_by_id: Optional[UUID] = None
    """ID of the user who created the prompt."""

    workspace_id: Optional[UUID] = None
    """ID of the workspace this prompt belongs to."""


class PromptCreate(PromptBase):
    """Schema for creating a new prompt. Inherits all fields from PromptBase."""

    created_by_id: Optional[UUID] = None
    """ID of the user who created the prompt. If not provided, will be set to the current user."""

    workspace_id: Optional[UUID] = None
    """ID of the workspace this prompt belongs to. If not provided, will be set to the current workspace."""


class PromptUpdate(BaseModel):
    """Schema for updating an existing prompt. All fields are optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    """Updated prompt name. Must be between 1 and 100 characters if provided."""

    prompt_id: Optional[str] = Field(None, min_length=1, max_length=100)
    """Updated prompt identifier."""

    type: Optional[str] = Field(None, min_length=1, max_length=50)
    """Updated prompt type."""

    prompt: Optional[str] = Field(None, min_length=1)
    """Updated prompt content."""


class PromptInDB(PromptBase):
    """Schema representing a prompt as stored in the database. Includes database-specific fields."""

    id: UUID
    """Unique identifier for the prompt in the database."""

    created_at: datetime
    """Timestamp when the prompt was created."""

    updated_at: datetime
    """Timestamp when the prompt was last updated."""

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class Prompt(PromptInDB):
    """Schema for prompt data returned in API responses."""

    pass
