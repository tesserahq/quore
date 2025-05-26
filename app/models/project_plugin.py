from app.models.mixins import TimestampMixin
from sqlalchemy import Column, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.db import Base


class ProjectPlugin(Base, TimestampMixin):
    """ProjectPlugin model for project-level plugin configurations."""

    __tablename__ = "project_plugins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    plugin_id = Column(UUID(as_uuid=True), ForeignKey("plugins.id"), nullable=False)
    is_enabled = Column(Boolean, default=True)
    config = Column(JSONB, nullable=True)  # Project-specific plugin configuration

    # Unique constraint to ensure a plugin can only be installed once per project
    __table_args__ = (
        UniqueConstraint("project_id", "plugin_id", name="uq_project_plugin"),
    )

    # Relationships
    project = relationship("Project", back_populates="plugins")
    plugin = relationship("Plugin", back_populates="project_plugins")
    enabled_tools = relationship(
        "ProjectPluginTool",
        back_populates="project_plugin",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<ProjectPlugin(project_id={self.project_id}, plugin_id={self.plugin_id})>"
        )
