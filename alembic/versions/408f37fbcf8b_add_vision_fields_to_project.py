"""add vision fields to project

Revision ID: 408f37fbcf8b
Revises: d9067bce9b24
Create Date: 2025-07-04 19:04:02.934294

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "408f37fbcf8b"
down_revision: Union[str, None] = "d9067bce9b24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "projects", sa.Column("vision_llm_provider", sa.String(), nullable=True)
    )
    op.add_column("projects", sa.Column("vision_model", sa.String(), nullable=True))
    op.add_column(
        "projects", sa.Column("vision_analysis_prompt", sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("projects", "vision_llm_provider")
    op.drop_column("projects", "vision_model")
    op.drop_column("projects", "vision_analysis_prompt")
