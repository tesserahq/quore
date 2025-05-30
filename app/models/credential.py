from app.models.mixins import TimestampMixin
from sqlalchemy import Column, String, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db import Base


class Credential(Base, TimestampMixin):
    """Credential model for storing encrypted credentials."""

    __tablename__ = "credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    encrypted_data = Column(
        LargeBinary, nullable=False
    )  # encrypted blob of all secret fields
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )

    # Relationships
    created_by = relationship("User", back_populates="credentials")
    workspace = relationship("Workspace", back_populates="credentials")
    plugins = relationship("Plugin", back_populates="credential")

    def __repr__(self):
        return f"<Credential(id={self.id}, name={self.name}, type={self.type}, workspace_id={self.workspace_id})>"
