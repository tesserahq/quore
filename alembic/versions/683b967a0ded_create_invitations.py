"""create invitations

Revision ID: 683b967a0ded
Revises: 65ab689e7bb2
Create Date: 2025-08-03 21:00:56.880506

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "683b967a0ded"
down_revision: Union[str, None] = "fbbfd4b09ee7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "invitations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("inviter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["inviter_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )
    op.create_index(
        "idx_invitations_workspace_id",
        "invitations",
        ["workspace_id"],
    )
    op.create_index(
        "idx_invitations_inviter_id",
        "invitations",
        ["inviter_id"],
    )

    op.add_column(
        "memberships",
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_foreign_key(
        "fk_memberships_created_by_id",
        "memberships",
        "users",
        ["created_by_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("invitations")
    op.drop_column("memberships", "created_by_id")
