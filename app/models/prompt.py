from app.models.mixins import TimestampMixin
from sqlalchemy import Column, String, ForeignKey, LargeBinary, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db import Base


class Prompt(Base, TimestampMixin):
    """Prompt model for storing prompts."""

    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    prompt_id = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )

    # Relationships
    created_by = relationship("User", back_populates="prompts")
    workspace = relationship("Workspace", back_populates="prompts")

    # Constraints
    __table_args__ = (UniqueConstraint("prompt_id", name="uq_prompts_prompt_id"),)

    def __repr__(self):
        return f"<Prompt(id={self.id}, name={self.name}, type={self.type}, workspace_id={self.workspace_id})>"
