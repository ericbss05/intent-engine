"""user_profile and consents

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_profile",
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("adult_confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "ai_assist_consent", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("ai_assist_consent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_user_profile")),
    )
    op.create_table(
        "consents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False),
        sa.Column("version_text", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_profile.user_id"],
            name=op.f("fk_consents_user_id_user_profile"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_consents")),
    )
    op.create_index("ix_consents_user_id_kind", "consents", ["user_id", "kind"])


def downgrade() -> None:
    op.drop_index("ix_consents_user_id_kind", table_name="consents")
    op.drop_table("consents")
    op.drop_table("user_profile")
