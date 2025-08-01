"""Add labels to projects

Revision ID: fbbfd4b09ee7
Revises: 2550d4723c64
Create Date: 2025-08-01 10:44:00.712788

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "fbbfd4b09ee7"
down_revision: Union[str, None] = "2550d4723c64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add the column with nullable=True first
    op.add_column(
        "projects",
        sa.Column("labels", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    # Update existing records to have an empty JSON object
    op.execute("UPDATE projects SET labels = '{}' WHERE labels IS NULL")

    # Now make the column non-nullable
    op.alter_column("projects", "labels", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("projects", "labels")
