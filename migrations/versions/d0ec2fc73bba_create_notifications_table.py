"""create notifications table

Revision ID: d0ec2fc73bba
Revises: dd08a0fabc3c
Create Date: 2021-07-07 19:45:00.024474

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d0ec2fc73bba"
down_revision = "dd08a0fabc3c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "notifications",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("token", sa.String(length=163), nullable=False),
        sa.Column("endpoint", sa.String(length=100), nullable=True),
        sa.Column("topic", sa.String(length=6), nullable=False),
        sa.Column("badge_type", sa.String(length=3), nullable=False),
        sa.Column(
            "data",
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite"),
            nullable=False,
        ),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("is_pending", sa.Boolean(), nullable=False),
        sa.Column("status", sa.SmallInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_notifications_status"), "notifications", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_notifications_topic"), "notifications", ["topic"], unique=False
    )
    op.create_index(
        op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_topic"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_status"), table_name="notifications")
    op.drop_table("notifications")
