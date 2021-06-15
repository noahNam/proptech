"""create ref-notification table

Revision ID: 80f2d6eebad0
Revises: 24b8fa736f0f
Create Date: 2021-05-25 18:13:21.964296

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "80f2d6eebad0"
down_revision = "4a93dd41716d"
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
        sa.Column("category", sa.String(length=6), nullable=False),
        sa.Column(
            "data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("is_pending", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "devices",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("os", sa.String(length=3), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_auth", sa.Boolean(), nullable=False),
        sa.Column("phone_number", sa.String(length=11), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "device_tokens",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("device_id", sa.BigInteger(), nullable=False),
        sa.Column("token", sa.String(length=163), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"],),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("device_tokens")
    op.drop_table("devices")
    op.drop_table("notifications")
