"""create promotions table

Revision ID: 072ad674bd49
Revises: b5d344d6d419
Create Date: 2021-07-31 19:55:58.101041

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "072ad674bd49"
down_revision = "b5d344d6d419"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "promotions",
        sa.Column(
            "id", sa.SmallInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("type", sa.String(length=4), nullable=False),
        sa.Column("div", sa.String(length=5), nullable=False),
        sa.Column("max_count", sa.SmallInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "promotion_houses",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("promotion_id", sa.SmallInteger(), nullable=False),
        sa.Column("house_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["promotion_id"], ["promotions.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_promotion_houses_house_id"),
        "promotion_houses",
        ["house_id"],
        unique=False,
    )
    op.create_table(
        "promotion_usage_counts",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("promotion_id", sa.SmallInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("usage_count", sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(["promotion_id"], ["promotions.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_promotion_usage_counts_user_id"),
        "promotion_usage_counts",
        ["user_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_promotion_usage_counts_user_id"), table_name="promotion_usage_counts"
    )
    op.drop_table("promotion_usage_counts")
    op.drop_index(op.f("ix_promotion_houses_house_id"), table_name="promotion_houses")
    op.drop_table("promotion_houses")
    op.drop_table("promotions")
