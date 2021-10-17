"""add column house_type_ranks

Revision ID: 8241c39d8164
Revises: ddf29843d9db
Create Date: 2021-10-14 15:44:47.425696

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "8241c39d8164"
down_revision = "ddf29843d9db"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "house_type_ranks",
        sa.Column("competition", sa.Integer(), nullable=True, server_default="0"),
    )


def downgrade():
    op.drop_column("house_type_ranks", "competition")
