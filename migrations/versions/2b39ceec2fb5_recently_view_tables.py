"""recently_view_tables

Revision ID: 2b39ceec2fb5
Revises: da750a6dd84b
Create Date: 2021-07-21 17:13:28.242204

"""
from alembic import op
import sqlalchemy as sa

revision = "2b39ceec2fb5"
down_revision = "da750a6dd84b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "recently_views",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("house_id", sa.BigInteger(), nullable=False),
        sa.Column("type", sa.SmallInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("recently_views")
