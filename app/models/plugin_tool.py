from app.models.mixins import TimestampMixin
from sqlalchemy import Column, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.db import Base


class PluginTool(Base, TimestampMixin):
    """PluginTool model for storing tool metadata and configuration."""

    __tablename__ = "plugin_tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plugin_id = Column(UUID(as_uuid=True), ForeignKey("plugins.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    input_schema = Column(JSONB, nullable=True)  # JSON Schema for input validation
    output_schema = Column(JSONB, nullable=True)  # JSON Schema for output validation
    tool_metadata = Column(JSONB, nullable=True)  # Additional tool metadata

    # Relationships
    plugin = relationship("Plugin", back_populates="tools")
    project_tools = relationship(
        "ProjectPluginTool", back_populates="tool", cascade="all, delete-orphan"
    )

    # Unique constraint to ensure a plugin can only be installed once per project
    __table_args__ = (UniqueConstraint("plugin_id", "name", name="uq_plugin_tool"),)

    def __repr__(self):
        return (
            f"<PluginTool(id={self.id}, name={self.name}, plugin_id={self.plugin_id})>"
        )
