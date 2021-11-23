"""add column private_area to predicted_competitions table

Revision ID: 7b0457032180
Revises: c8dc095374f5
Create Date: 2021-11-22 18:10:28.946997

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7b0457032180"
down_revision = "c8dc095374f5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "predicted_competitions", sa.Column("private_area", sa.Float(), nullable=True)
    )


def downgrade():
    op.drop_column("predicted_competitions", "private_area")
