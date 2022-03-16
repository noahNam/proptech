"""add_is_checked_to_public_sales

Revision ID: 58192dd86224
Revises: 23b09934b59e
Create Date: 2022-03-16 15:26:49.252756

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "58192dd86224"
down_revision = "23b09934b59e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "public_sales",
        sa.Column(
            "is_checked",
            sa.Boolean(),
            nullable=False,
            default=False,
            server_default="false",
        ),
    )


def downgrade():
    op.drop_column("public_sales", "is_checked")
