from app.models.mixins import TimestampMixin
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.db import Base
from app.constants.plugin_states import PluginState


class Plugin(Base, TimestampMixin):
    """Plugin model for storing plugin metadata and configuration."""

    __tablename__ = "plugins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    repository_url = Column(String, nullable=True)
    version = Column(String(50), nullable=True)  # Git tag or commit hash
    commit_hash = Column(
        String(50), nullable=True
    )  # Specific commit hash if version is a tag
    # state: Mapped[PluginState] = Column(SQLEnum(PluginState), nullable=False, default=PluginState.REGISTERED)
    state = Column(SQLEnum(PluginState), nullable=False, default=PluginState.REGISTERED)
    endpoint_url = Column(
        String, nullable=True
    )  # Runtime endpoint (e.g. http://localhost:5001)
    plugin_metadata = Column(
        JSONB, nullable=True
    )  # Additional plugin metadata from MCP discovery
    credential_id = Column(
        UUID(as_uuid=True), ForeignKey("credentials.id"), nullable=True
    )  # Reference to stored credential
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )  # Required workspace association

    # Relationships
    workspace = relationship("Workspace", back_populates="plugins")
    credential = relationship("Credential", back_populates="plugins")
    tools = relationship(
        "PluginTool", back_populates="plugin", cascade="all, delete-orphan"
    )
    project_plugins = relationship(
        "ProjectPlugin", back_populates="plugin", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Plugin(id={self.id}, name={self.name}, workspace_id={self.workspace_id}, state={self.state})>"
