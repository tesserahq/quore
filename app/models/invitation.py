from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from app.db import Base
from app.constants.membership import MembershipRoles
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class Invitation(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "invitations"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), nullable=False)
    workspace_id = Column(
        PostgresUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    role = Column(String(50), nullable=False)
    message = Column(Text, nullable=True)
    inviter_id = Column(
        PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    expires_at = Column(DateTime, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="invitations")
    inviter = relationship(
        "User", foreign_keys=[inviter_id], back_populates="invitations"
    )

    @property
    def is_expired(self) -> bool:
        """Check if the invitation has expired."""
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expires_at

    @property
    def is_valid(self) -> bool:
        """Check if the invitation is valid (not expired)."""
        return not self.is_expired
