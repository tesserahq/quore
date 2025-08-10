from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging

from app.db import get_db
from app.schemas.prompt import Prompt, PromptCreate, PromptUpdate
from app.services.prompt_service import PromptService
from app.schemas.common import ListResponse
from app.utils.auth import get_current_user
from app.models.workspace import Workspace
from app.models.prompt import Prompt as PromptModel
from app.routers.utils.dependencies import get_workspace_by_id
from app.core.logging_config import get_logger

logger = get_logger()

# Workspace-scoped router
workspace_router = APIRouter(
    prefix="/workspaces/{workspace_id}/prompts", tags=["prompts"]
)

# Direct prompt access router
prompt_router = APIRouter(prefix="/prompts", tags=["prompts"])


def get_prompt_by_id(
    prompt_id: UUID,
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
) -> PromptModel:
    """Get a prompt by ID within a workspace scope."""
    prompt = PromptService(db).get_prompt(prompt_id)
    if prompt is None or prompt.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


def get_prompt_direct(
    prompt_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> PromptModel:
    """Get a prompt directly by ID, checking user permissions."""
    logger.info(f"Getting prompt {prompt_id} for user {current_user.id}")

    prompt_service = PromptService(db)
    prompt = prompt_service.get_prompt(prompt_id)
    if prompt is None:
        logger.warning(f"Prompt {prompt_id} not found")
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Check if user has access to the workspace containing this prompt
    user_workspace_ids = [m.workspace_id for m in current_user.memberships]
    if prompt.workspace_id not in user_workspace_ids:
        logger.warning(
            f"User {current_user.id} attempted to access prompt {prompt_id} from unauthorized workspace {prompt.workspace_id}"
        )
        raise HTTPException(
            status_code=403, detail="Not authorized to access this prompt"
        )

    return prompt


@workspace_router.get("", response_model=ListResponse[Prompt])
def list_workspace_prompts(
    workspace: Workspace = Depends(get_workspace_by_id),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List prompts in a workspace."""
    prompts = PromptService(db).get_prompts_by_workspace(
        workspace.id, skip=skip, limit=limit
    )
    return ListResponse(data=prompts)


@prompt_router.get("", response_model=ListResponse[Prompt])
def list_prompts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all prompts the user has access to."""
    # Get all workspaces the user is a member of
    workspace_ids = [m.workspace_id for m in current_user.memberships]
    filters = {"workspace_id": {"operator": "in", "value": workspace_ids}}
    prompts = PromptService(db).search(filters)
    return ListResponse(data=prompts)


@workspace_router.post("", response_model=Prompt, status_code=status.HTTP_201_CREATED)
def create_workspace_prompt(
    prompt_data: PromptCreate,
    workspace: Workspace = Depends(get_workspace_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new prompt in a workspace."""
    # Override workspace_id and created_by_id for security
    prompt_data.workspace_id = workspace.id
    prompt_data.created_by_id = current_user.id

    return PromptService(db).create_prompt(prompt_data)


@workspace_router.get("/{prompt_id}", response_model=Prompt)
def get_workspace_prompt(
    prompt: PromptModel = Depends(get_prompt_by_id),
):
    """Get a specific prompt in a workspace."""
    return prompt


@prompt_router.get("/{prompt_id}", response_model=Prompt)
def get_prompt(
    prompt: PromptModel = Depends(get_prompt_direct),
):
    """Get a specific prompt by ID."""
    return prompt


@workspace_router.put("/{prompt_id}", response_model=Prompt)
def update_workspace_prompt(
    prompt_update: PromptUpdate,
    prompt: PromptModel = Depends(get_prompt_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a prompt in a workspace."""
    updated_prompt = PromptService(db).update_prompt(prompt.id, prompt_update)
    if updated_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated_prompt


@prompt_router.put("/{prompt_id}", response_model=Prompt)
def update_prompt(
    prompt_update: PromptUpdate,
    prompt: PromptModel = Depends(get_prompt_direct),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a prompt by ID."""
    updated_prompt = PromptService(db).update_prompt(prompt.id, prompt_update)
    if updated_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated_prompt


@prompt_router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(
    prompt: PromptModel = Depends(get_prompt_direct),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a prompt by ID."""
    PromptService(db).delete_prompt(prompt.id)


# Additional convenience endpoints


@workspace_router.get("/types/{prompt_type}", response_model=ListResponse[Prompt])
def list_prompts_by_type(
    prompt_type: str,
    workspace: Workspace = Depends(get_workspace_by_id),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List prompts by type in a workspace."""
    prompts = PromptService(db).get_prompts_by_type(
        prompt_type, workspace_id=workspace.id, skip=skip, limit=limit
    )
    return ListResponse(data=prompts)


@workspace_router.get("/creator/{creator_id}", response_model=ListResponse[Prompt])
def list_prompts_by_creator(
    creator_id: UUID,
    workspace: Workspace = Depends(get_workspace_by_id),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List prompts by creator in a workspace."""
    prompts = PromptService(db).get_prompts_by_creator(
        creator_id, workspace_id=workspace.id, skip=skip, limit=limit
    )
    return ListResponse(data=prompts)
