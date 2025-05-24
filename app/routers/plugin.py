from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.db import get_db
from app.schemas.plugin import PluginResponse, PluginCreate
from app.services.plugin_registry import PluginRegistryService
from app.schemas.common import ListResponse

router = APIRouter(tags=["plugins"])


@router.get(
    "/workspaces/{workspace_id}/plugins", response_model=ListResponse[PluginResponse]
)
def list_workspace_plugins(
    workspace_id: UUID,
    db: Session = Depends(get_db),
):
    """List all plugins available for a workspace (both system plugins and workspace-specific plugins)."""
    plugins = PluginRegistryService(db).get_workspace_plugins(workspace_id)
    return ListResponse(data=plugins)


@router.post("/workspaces/{workspace_id}/plugins", response_model=PluginResponse)
def create_workspace_plugin(
    workspace_id: UUID,
    plugin_data: PluginCreate,
    db: Session = Depends(get_db),
):
    """Create a new plugin for a workspace."""
    plugin_data.workspace_id = workspace_id
    plugin = PluginRegistryService(db).register_plugin(plugin_data)
    return plugin


@router.get(
    "/projects/{project_id}/plugins", response_model=ListResponse[PluginResponse]
)
def list_project_plugins(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    """List all enabled plugins for a project."""
    plugins = PluginRegistryService(db).get_project_plugins(project_id)
    return ListResponse(data=plugins)


@router.post(
    "/projects/{project_id}/plugins/{plugin_id}", response_model=PluginResponse
)
def enable_project_plugin(
    project_id: UUID,
    plugin_id: UUID,
    config: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
):
    """Enable a plugin in a project."""
    service = PluginRegistryService(db)
    project_plugin = service.enable_plugin_in_project(project_id, plugin_id, config)
    return service.get_plugin(plugin_id)
