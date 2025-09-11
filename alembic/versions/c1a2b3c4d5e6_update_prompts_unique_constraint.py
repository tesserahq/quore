"""update prompts unique constraint

Revision ID: c1a2b3c4d5e6
Revises: 79b2291772fd, 2550d4723c64
Create Date: 2025-09-11 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1a2b3c4d5e6"
# Merge the two heads to continue on a single linear history
down_revision = ("79b2291772fd", "2550d4723c64")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop old unique constraint on prompt_id only
    op.drop_constraint("uq_prompts_prompt_id", "prompts", type_="unique")

    # Add new composite unique constraint on (workspace_id, prompt_id)
    op.create_unique_constraint(
        "uq_prompts_workspace_id_prompt_id",
        "prompts",
        ["workspace_id", "prompt_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Revert to old unique constraint on prompt_id only
    op.drop_constraint(
        "uq_prompts_workspace_id_prompt_id", "prompts", type_="unique"
    )
    op.create_unique_constraint("uq_prompts_prompt_id", "prompts", ["prompt_id"])

