"""add global and enable fields

Revision ID: 40c926724af0
Revises: add_wills_fts
Create Date: 2025-08-10 22:19:33.116820

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "40c926724af0"
down_revision: Union[str, None] = "1a2b3c4d5e6f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "plugins", sa.Column("is_global", sa.Boolean(), nullable=False, default=False)
    )
    op.add_column(
        "plugins", sa.Column("is_enabled", sa.Boolean(), nullable=False, default=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("plugins", "is_enabled")
    op.drop_column("plugins", "is_global")
