"""Update prompt_id unique constrain

Revision ID: 4b166d9ede11
Revises: 03599d07def1
Create Date: 2025-09-18 12:10:16.850639

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4b166d9ede11"
down_revision: Union[str, None] = "03599d07def1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop old unique constraint on prompt_id only
    op.drop_constraint("uq_prompts_workspace_id_prompt_id", "prompts", type_="unique")

    # Add new composite unique constraint on (workspace_id, prompt_id)
    op.create_unique_constraint(
        "uq_prompts_workspace_id_prompt_id",
        "prompts",
        ["workspace_id", "prompt_id", "deleted_at"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop old unique constraint on prompt_id only
    op.drop_constraint("uq_prompts_workspace_id_prompt_id", "prompts", type_="unique")
    op.create_unique_constraint(
        "uq_prompts_workspace_id_prompt_id", "prompts", ["prompt_id", "workspace_id"]
    )
