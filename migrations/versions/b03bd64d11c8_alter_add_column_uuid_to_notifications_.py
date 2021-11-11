"""alter add_column_uuid_to_notifications table

Revision ID: b03bd64d11c8
Revises: fb54c95682e7
Create Date: 2021-11-11 16:08:59.342976

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b03bd64d11c8"
down_revision = "fb54c95682e7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "notifications", sa.Column("uuid", sa.String(length=36), nullable=True)
    )


def downgrade():
    op.drop_column("notifications", "uuid")
