"""alter phone_number column

Revision ID: eaa096feb2b8
Revises: 1342ddd4b73e
Create Date: 2022-03-28 16:53:54.447620

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'eaa096feb2b8'
down_revision = '1342ddd4b73e'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "devices",
        "phone_number",
        existing_type=sa.String(length=11),
        type_=sa.String(length=75),
    )


def downgrade():
    op.alter_column(
        "devices",
        "phone_number",
        existing_type=sa.String(length=75),
        type_=sa.String(length=11),
    )

