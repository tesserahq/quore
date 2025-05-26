from app.models.mixins import TimestampMixin
from sqlalchemy import Column, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.db import Base


class ProjectPluginTool(Base, TimestampMixin):
    """ProjectPluginTool model for project-level tool configurations."""

    __tablename__ = "project_plugin_tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_plugin_id = Column(
        UUID(as_uuid=True), ForeignKey("project_plugins.id"), nullable=False
    )
    tool_id = Column(UUID(as_uuid=True), ForeignKey("plugin_tools.id"), nullable=False)
    is_enabled = Column(Boolean, default=True)
    config = Column(JSONB, nullable=True)  # Project-specific tool configuration

    # Relationships
    project_plugin = relationship("ProjectPlugin", back_populates="enabled_tools")
    tool = relationship("PluginTool", back_populates="project_tools")

    def __repr__(self):
        return f"<ProjectPluginTool(project_plugin_id={self.project_plugin_id}, tool_id={self.tool_id})>"
