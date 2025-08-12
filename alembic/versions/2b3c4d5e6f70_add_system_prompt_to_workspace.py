"""add system_prompt to workspace

Revision ID: 2b3c4d5e6f70
Revises: aa11bb22cc33
Create Date: 2025-08-12 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2b3c4d5e6f70"
down_revision: Union[str, None] = "aa11bb22cc33"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "workspaces",
        sa.Column("system_prompt", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("workspaces", "system_prompt")
