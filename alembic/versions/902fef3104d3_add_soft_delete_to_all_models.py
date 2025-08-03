"""add soft delete to all models

Revision ID: 902fef3104d3
Revises: 683b967a0ded
Create Date: 2025-01-18 20:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "902fef3104d3"
down_revision: Union[str, None] = "683b967a0ded"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add deleted_at column to users table
    op.add_column("users", sa.Column("deleted_at", sa.DateTime, nullable=True))
    op.create_index("idx_users_deleted_at", "users", ["deleted_at"])
    
    # Add deleted_at column to workspaces table
    op.add_column("workspaces", sa.Column("deleted_at", sa.DateTime, nullable=True))
    op.create_index("idx_workspaces_deleted_at", "workspaces", ["deleted_at"])
    
    # Add deleted_at column to projects table
    op.add_column("projects", sa.Column("deleted_at", sa.DateTime, nullable=True))
    op.create_index("idx_projects_deleted_at", "projects", ["deleted_at"])
    
    # Add deleted_at column to memberships table
    op.add_column("memberships", sa.Column("deleted_at", sa.DateTime, nullable=True))
    op.create_index("idx_memberships_deleted_at", "memberships", ["deleted_at"])
    
    # Add deleted_at column to plugins table
    op.add_column("plugins", sa.Column("deleted_at", sa.DateTime, nullable=True))
    op.create_index("idx_plugins_deleted_at", "plugins", ["deleted_at"])
    
    # Add deleted_at column to project_plugins table
    op.add_column("project_plugins", sa.Column("deleted_at", sa.DateTime, nullable=True))
    op.create_index("idx_project_plugins_deleted_at", "project_plugins", ["deleted_at"])
    
    # Add deleted_at column to prompts table
    op.add_column("prompts", sa.Column("deleted_at", sa.DateTime, nullable=True))
    op.create_index("idx_prompts_deleted_at", "prompts", ["deleted_at"])
    
    # Add deleted_at column to credentials table
    op.add_column("credentials", sa.Column("deleted_at", sa.DateTime, nullable=True))
    op.create_index("idx_credentials_deleted_at", "credentials", ["deleted_at"])
    
    # Add deleted_at column to app_settings table
    op.add_column("app_settings", sa.Column("deleted_at", sa.DateTime, nullable=True))
    op.create_index("idx_app_settings_deleted_at", "app_settings", ["deleted_at"])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove deleted_at column and index from app_settings table
    op.drop_index("idx_app_settings_deleted_at", "app_settings")
    op.drop_column("app_settings", "deleted_at")
    
    # Remove deleted_at column and index from credentials table
    op.drop_index("idx_credentials_deleted_at", "credentials")
    op.drop_column("credentials", "deleted_at")
    
    # Remove deleted_at column and index from prompts table
    op.drop_index("idx_prompts_deleted_at", "prompts")
    op.drop_column("prompts", "deleted_at")
    
    # Remove deleted_at column and index from project_plugins table
    op.drop_index("idx_project_plugins_deleted_at", "project_plugins")
    op.drop_column("project_plugins", "deleted_at")
    
    # Remove deleted_at column and index from plugins table
    op.drop_index("idx_plugins_deleted_at", "plugins")
    op.drop_column("plugins", "deleted_at")
    
    # Remove deleted_at column and index from memberships table
    op.drop_index("idx_memberships_deleted_at", "memberships")
    op.drop_column("memberships", "deleted_at")
    
    # Remove deleted_at column and index from projects table
    op.drop_index("idx_projects_deleted_at", "projects")
    op.drop_column("projects", "deleted_at")
    
    # Remove deleted_at column and index from workspaces table
    op.drop_index("idx_workspaces_deleted_at", "workspaces")
    op.drop_column("workspaces", "deleted_at")
    
    # Remove deleted_at column and index from users table
    op.drop_index("idx_users_deleted_at", "users")
    op.drop_column("users", "deleted_at")