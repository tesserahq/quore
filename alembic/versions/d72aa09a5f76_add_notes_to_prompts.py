"""add notes to prompts

Revision ID: d72aa09a5f76
Revises: 9849583adcd0
Create Date: 2025-07-21 12:26:48.235626

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d72aa09a5f76"
down_revision: Union[str, None] = "9849583adcd0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("prompts", sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("prompts", "notes")
