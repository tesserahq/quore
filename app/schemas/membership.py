from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class MembershipBase(BaseModel):
    """Base membership model containing common membership attributes."""

    user_id: UUID
    """ID of the user who is a member of the workspace."""

    workspace_id: UUID
    """ID of the workspace the user is a member of."""

    role: str = "member"
    """Role of the user in the workspace. Defaults to 'member'. Other common roles include 'owner' and 'admin'."""


class MembershipCreate(MembershipBase):
    """Schema for creating a new membership. Inherits all fields from MembershipBase."""

    pass


class MembershipUpdate(BaseModel):
    """Schema for updating an existing membership. All fields are optional."""

    role: Optional[str] = None
    """Updated role for the user in the workspace."""


class MembershipInDB(MembershipBase):
    """Schema representing a membership as stored in the database. Includes database-specific fields."""

    id: UUID
    """Unique identifier for the membership in the database."""

    created_at: datetime
    """Timestamp when the membership was created."""

    updated_at: datetime
    """Timestamp when the membership was last updated."""

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
