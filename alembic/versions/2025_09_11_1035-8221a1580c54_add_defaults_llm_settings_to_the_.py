"""add defaults llm settings to the workspace

Revision ID: 8221a1580c54
Revises: 79b2291772fd
Create Date: 2025-09-11 10:35:04.199548

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8221a1580c54"
down_revision: Union[str, None] = "79b2291772fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "workspaces",
        sa.Column("default_llm_provider", sa.String(), nullable=True),
    )
    op.add_column(
        "workspaces",
        sa.Column("default_embed_model", sa.String(), nullable=True),
    )
    op.add_column(
        "workspaces",
        sa.Column("default_embed_dim", sa.Integer(), nullable=True),
    )
    op.add_column(
        "workspaces",
        sa.Column("default_llm", sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("workspaces", "default_llm_provider")
    op.drop_column("workspaces", "default_embed_model")
    op.drop_column("workspaces", "default_embed_dim")
    op.drop_column("workspaces", "default_llm")
