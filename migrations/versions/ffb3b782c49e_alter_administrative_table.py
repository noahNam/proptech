"""alter_administrative_table

Revision ID: ffb3b782c49e
Revises: 715454d6f019
Create Date: 2021-10-10 01:45:59.240199

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "ffb3b782c49e"
down_revision = "715454d6f019"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "administrative_divisions",
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="True"),
    )


def downgrade():
    op.drop_column("administrative_divisions", "is_available")
