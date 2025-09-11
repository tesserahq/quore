from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class AppSettingBase(BaseModel):
    """Base app setting model containing common app setting attributes."""

    id: Optional[UUID] = None
    """Unique identifier for the app setting. Defaults to None."""

    key: str
    """Setting key. Required field."""

    value: str
    """Setting value. Required field."""


class AppSettingCreate(AppSettingBase):
    """Schema for creating a new app setting. Inherits all fields from AppSettingBase."""

    pass


class AppSettingUpdate(BaseModel):
    """Schema for updating an existing app setting. All fields are optional."""

    key: Optional[str] = None
    """Updated setting key."""

    value: Optional[str] = None
    """Updated setting value."""


class AppSettingInDB(AppSettingBase):
    """Schema representing an app setting as stored in the database. Includes database-specific fields."""

    id: UUID
    """Unique identifier for the app setting in the database."""

    created_at: datetime
    """Timestamp when the app setting record was created."""

    updated_at: datetime
    """Timestamp when the app setting record was last updated."""

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class AppSetting(AppSettingInDB):
    """Schema for app setting data returned in API responses. Inherits all fields from AppSettingInDB."""

    pass
