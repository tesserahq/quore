from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from app.constants.plugin_states import PluginState


class PluginBase(BaseModel):
    """Base schema for plugin data."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    version: Optional[str] = None
    state: Optional[PluginState] = None
    state_description: Optional[str] = None
    endpoint_url: Optional[str] = None
    plugin_metadata: Optional[Dict[str, Any]] = None
    credential_id: Optional[UUID] = None
    tools: Optional[List[Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = None
    prompts: Optional[List[Dict[str, Any]]] = None
    workspace_id: Optional[UUID] = None  # Optional since it's set from URL parameter


class PluginCreate(PluginBase):
    """Schema for creating a new plugin."""

    pass


class PluginCreateRequest(BaseModel):
    """Schema for the request body when creating a plugin."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    endpoint_url: str = Field(..., min_length=1)
    version: Optional[str] = None
    credential_id: Optional[UUID] = None
    workspace_id: Optional[UUID] = None


class PluginUpdate(BaseModel):
    """Schema for updating an existing plugin."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    version: Optional[str] = None
    state: Optional[PluginState] = None
    state_description: Optional[str] = None
    endpoint_url: Optional[str] = None
    plugin_metadata: Optional[Dict[str, Any]] = None
    credential_id: Optional[UUID] = None
    tools: Optional[List[Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = None
    prompts: Optional[List[Dict[str, Any]]] = None


class PluginToolBase(BaseModel):
    """Base schema for plugin tool data."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    tool_metadata: Optional[Dict[str, Any]] = None


class PluginToolCreate(PluginToolBase):
    """Schema for creating a new plugin tool."""

    pass


class PluginToolUpdate(BaseModel):
    """Schema for updating an existing plugin tool."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    tool_metadata: Optional[Dict[str, Any]] = None


class PluginToolResponse(PluginToolBase):
    """Schema for plugin tool response."""

    id: UUID
    plugin_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PluginResponse(PluginBase):
    """Schema for plugin response."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PluginStatesResponse(BaseModel):
    """Schema for listing available plugin states."""

    states: List[Dict[str, str]] = Field(
        ...,
        description="List of available plugin states with their values and descriptions",
    )
