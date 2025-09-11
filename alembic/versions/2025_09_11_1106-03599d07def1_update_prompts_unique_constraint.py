"""update prompts unique constraint

Revision ID: 03599d07def1
Revises: 8221a1580c54
Create Date: 2025-09-11 11:06:23.187565

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "03599d07def1"
down_revision: Union[str, None] = "8221a1580c54"
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
    op.drop_constraint("uq_prompts_workspace_id_prompt_id", "prompts", type_="unique")
    op.create_unique_constraint("uq_prompts_prompt_id", "prompts", ["prompt_id"])
