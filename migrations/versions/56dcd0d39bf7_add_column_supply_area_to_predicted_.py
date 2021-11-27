"""add column supply_area to predicted_competitions table

Revision ID: 56dcd0d39bf7
Revises: 7b0457032180
Create Date: 2021-11-28 00:17:37.357740

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "56dcd0d39bf7"
down_revision = "7b0457032180"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "predicted_competitions", sa.Column("supply_area", sa.Float(), nullable=True)
    )


def downgrade():
    op.drop_column("predicted_competitions", "supply_area")
