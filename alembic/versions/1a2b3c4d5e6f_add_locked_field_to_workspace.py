"""add locked field to workspace

Revision ID: 1a2b3c4d5e6f
Revises: 902fef3104d3
Create Date: 2025-01-18 21:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1a2b3c4d5e6f"
down_revision: Union[str, None] = "902fef3104d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add locked column to workspaces table
    op.add_column(
        "workspaces",
        sa.Column("locked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove locked column from workspaces table
    op.drop_column("workspaces", "locked")
