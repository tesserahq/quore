from app.models.mixins import TimestampMixin
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db import Base


class Workspace(Base, TimestampMixin):
    """Workspace model for the application."""

    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    description = Column(String, nullable=True)
    logo = Column(String, nullable=True)  # We'll handle file uploads separately
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="workspaces")
    updated_by = relationship("User", back_populates="workspaces")
    memberships = relationship("Membership", back_populates="workspace")
    projects = relationship("Project", back_populates="workspace")
