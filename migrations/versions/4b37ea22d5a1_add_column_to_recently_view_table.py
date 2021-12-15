"""add column to recently view table

Revision ID: 4b37ea22d5a1
Revises: 79ffd3f30f04
Create Date: 2021-12-15 16:55:33.924308

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4b37ea22d5a1"
down_revision = "79ffd3f30f04"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "recently_views", sa.Column("updated_at", sa.DateTime(), nullable=True)
    )
    op.alter_column(
        "recently_views",
        "updated_at",
        server_default=sa.text("now()"),
        type_=postgresql.TIMESTAMP(timezone=True),
    )
    op.add_column(
        "recently_views", sa.Column("is_available", sa.Boolean(), nullable=True)
    )
    op.create_index(
        op.f("ix_recently_views_house_id"), "recently_views", ["house_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_recently_views_house_id"), table_name="recently_views")
    op.drop_column("recently_views", "is_available")
    op.drop_column("recently_views", "updated_at")
