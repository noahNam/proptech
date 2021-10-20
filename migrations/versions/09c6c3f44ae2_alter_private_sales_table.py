"""alter_private_sales_table

Revision ID: 09c6c3f44ae2
Revises: 8241c39d8164
Create Date: 2021-10-18 00:49:14.930549

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "09c6c3f44ae2"
down_revision = "8241c39d8164"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "private_sales",
        sa.Column(
            "trade_status", sa.SmallInteger(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "private_sales",
        sa.Column(
            "deposit_status", sa.SmallInteger(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "private_sales",
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="true"),
    )


def downgrade():
    op.drop_column("private_sales", "deposit_status")
    op.drop_column("private_sales", "trade_status")
    op.drop_column("private_sales", "is_available")
