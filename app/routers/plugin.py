from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from uuid import UUID

from app.commands.initialize_plugin import initialize_plugin_command
from app.db import get_db
from app.models.plugin import Plugin
from app.schemas.plugin import (
    PluginCreateRequest,
    PluginResponse,
    PluginCreate,
    PluginUpdate,
    PluginStatesResponse,
)
from app.services.plugin import PluginService
from app.schemas.common import ListResponse
from app.models.workspace import Workspace
from app.models.project import Project
from app.utils.dependencies import (
    get_workspace_by_id,
    get_project_by_id,
    get_plugin_by_id,
)
from app.core.mcp_client import MCPClient
from app.constants.plugin_states import PluginState

router = APIRouter(tags=["plugins"])


@router.get(
    "/workspaces/{workspace_id}/plugins", response_model=ListResponse[PluginResponse]
)
def list_workspace_plugins(
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
):
    """List all plugins available for a workspace (both system plugins and workspace-specific plugins)."""
    plugins = PluginService(db).get_workspace_plugins(UUID(str(workspace.id)))
    return ListResponse(data=plugins)


@router.post("/workspaces/{workspace_id}/plugins", response_model=PluginResponse)
def create_workspace_plugin(
    plugin_data: PluginCreateRequest,
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
):
    """Create a new plugin for a workspace."""
    plugin_data.workspace_id = UUID(str(workspace.id))
    plugin = initialize_plugin_command(db, PluginCreate(**plugin_data.model_dump()))
    return plugin


@router.get(
    "/projects/{project_id}/plugins", response_model=ListResponse[PluginResponse]
)
def list_project_plugins(
    project: Project = Depends(get_project_by_id),
    db: Session = Depends(get_db),
):
    """List all enabled plugins for a project."""
    plugins = PluginService(db).get_project_plugins(UUID(str(project.id)))
    return ListResponse(data=plugins)


@router.post(
    "/projects/{project_id}/plugins/{plugin_id}", response_model=PluginResponse
)
def enable_project_plugin(
    project: Project = Depends(get_project_by_id),
    plugin: Plugin = Depends(get_plugin_by_id),
    config: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
):
    """Enable a plugin in a project."""
    service = PluginService(db)
    service.enable_plugin_in_project(
        UUID(str(project.id)), UUID(str(plugin.id)), config
    )
    return service.get_plugin(UUID(str(plugin.id)))


@router.put("/plugins/{plugin_id}", response_model=PluginResponse)
def update_plugin(
    plugin_data: PluginUpdate,
    plugin: Plugin = Depends(get_plugin_by_id),
    db: Session = Depends(get_db),
):
    """Update a plugin's metadata."""
    service = PluginService(db)
    plugin = service.update_plugin(UUID(str(plugin.id)), plugin_data)
    return plugin


@router.get("/plugins/{plugin_id}/inspect/tools")
async def inspect_tools_plugin(
    plugin: Plugin = Depends(get_plugin_by_id),
    db: Session = Depends(get_db),
):
    """Get plugins tools directly from the MCP server."""
    if not plugin.endpoint_url:
        raise HTTPException(status_code=422, detail="Plugin endpoint URL is not set")

    async with MCPClient(plugin.endpoint_url) as client:
        return await client.list_tools()


@router.get("/plugins/{plugin_id}/inspect/prompts")
async def inspect_prompts_plugin(
    plugin: Plugin = Depends(get_plugin_by_id),
    db: Session = Depends(get_db),
):
    """Get plugins prompts directly from the MCP server."""
    if not plugin.endpoint_url:
        raise HTTPException(status_code=422, detail="Plugin endpoint URL is not set")

    async with MCPClient(plugin.endpoint_url) as client:
        return await client.list_prompts()


@router.get("/plugins/{plugin_id}/inspect/resources")
async def inspect_resources_plugin(
    plugin: Plugin = Depends(get_plugin_by_id),
    db: Session = Depends(get_db),
):
    """Get plugins resources directly from the MCP server."""
    if not plugin.endpoint_url:
        raise HTTPException(status_code=422, detail="Plugin endpoint URL is not set")

    async with MCPClient(plugin.endpoint_url) as client:
        return await client.list_resources()


@router.get("/plugins/states", response_model=PluginStatesResponse)
def list_plugin_states():
    """Get a list of all available plugin states with their descriptions."""
    states = [
        {"value": state.value, "description": state.__doc__ or state.value}
        for state in PluginState
    ]
    return PluginStatesResponse(states=states)
