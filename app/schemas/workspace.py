from app.schemas.user import UserDetails
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class WorkspaceBase(BaseModel):
    """Base workspace model containing common workspace attributes."""

    name: str = Field(..., min_length=1, max_length=100)
    """Name of the workspace. Must be between 1 and 100 characters."""

    description: Optional[str] = None
    """Optional description of the workspace."""

    logo: Optional[str] = None
    """Optional URL to the workspace's logo image."""

    identifier: Optional[str] = Field(None, min_length=1, max_length=100)
    """Optional unique identifier for the workspace. Must be a slug-like string."""

    created_by_id: Optional[UUID] = None
    """ID of the user who created the workspace."""


class WorkspaceCreate(WorkspaceBase):
    """Schema for creating a new workspace. Inherits all fields from WorkspaceBase."""

    created_by_id: Optional[UUID] = None
    """ID of the user who created the workspace. If not provided, will be set to the current user."""


class WorkspaceUpdate(BaseModel):
    """Schema for updating an existing workspace. All fields are optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    """Updated workspace name. Must be between 1 and 100 characters if provided."""

    description: Optional[str] = None
    """Updated workspace description."""

    logo: Optional[str] = None
    """Updated workspace logo URL."""

    identifier: Optional[str] = Field(None, min_length=1, max_length=100)
    """Updated workspace identifier. Must be a unique slug-like string if provided."""


class WorkspaceInDB(WorkspaceBase):
    """Schema representing a workspace as stored in the database. Includes database-specific fields."""

    id: UUID
    """Unique identifier for the workspace in the database."""

    created_at: datetime
    """Timestamp when the workspace was created."""

    updated_at: datetime
    """Timestamp when the workspace was last updated."""

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class Workspace(WorkspaceInDB):
    """Schema for workspace data returned in API responses. Includes creator details."""

    created_by: Optional[UserDetails]
    """Details of the user who created the workspace."""
