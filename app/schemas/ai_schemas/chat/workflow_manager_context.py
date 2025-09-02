from typing import Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.models.project import Project


class WorkflowManagerContext(BaseModel):
    """Context object for WorkflowManager initialization.

    This schema encapsulates all the parameters needed to initialize a WorkflowManager,
    making the constructor cleaner and more maintainable.
    """

    db_session: Session = Field(
        ..., description="Database session for database operations"
    )

    project: Project = Field(
        ..., description="Project instance containing configuration and settings"
    )

    access_token: Optional[str] = Field(
        default=None,
        description="Access token for authentication with external services",
    )

    system_prompt_id: Optional[Union[UUID, str]] = Field(
        default=None,
        description="ID of the system prompt to use (overrides project's default system prompt). Can be either UUID or string prompt_id.",
    )

    initial_state: Optional[dict] = Field(
        default=None,
        description="Initial state for the workflow",
    )

    disable_tools: bool = Field(
        default=False,
        description="Whether to disable tools",
    )

    class Config:
        arbitrary_types_allowed = True  # Allow SQLAlchemy Session and Project objects
