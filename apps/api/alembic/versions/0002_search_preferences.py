"""search_preferences

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "search_preferences",
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("contract_type", sa.String(16), nullable=False),
        sa.Column("duration_months", sa.Integer(), nullable=False),
        sa.Column("target_role", sa.String(100), nullable=False),
        sa.Column("sectors", postgresql.JSONB(), nullable=False),
        sa.Column("zone", postgresql.JSONB(), nullable=False),
        sa.Column("company_size", postgresql.JSONB(), nullable=False),
        sa.Column(
            "priorities", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False
        ),
        sa.Column(
            "excluded_sirens",
            postgresql.JSONB(),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "contract_type in ('stage', 'alternance')",
            name=op.f("ck_search_preferences_contract_type"),
        ),
        sa.CheckConstraint(
            "duration_months between 1 and 36", name=op.f("ck_search_preferences_duration_months")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_profile.user_id"],
            name=op.f("fk_search_preferences_user_id_user_profile"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_search_preferences")),
    )


def downgrade() -> None:
    op.drop_table("search_preferences")
