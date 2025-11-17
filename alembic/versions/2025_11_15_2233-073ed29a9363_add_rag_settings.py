"""Add RAG settings

Revision ID: 073ed29a9363
Revises: 4b166d9ede11
Create Date: 2025-11-15 22:33:42.202153

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "073ed29a9363"
down_revision: Union[str, None] = "4b166d9ede11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "projects", sa.Column("rag_settings", postgresql.JSONB(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("projects", "rag_settings")
