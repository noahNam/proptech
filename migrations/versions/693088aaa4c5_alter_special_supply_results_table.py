"""alter special_supply_results table

Revision ID: 693088aaa4c5
Revises: 4b37ea22d5a1
Create Date: 2022-01-05 14:34:47.847574

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "693088aaa4c5"
down_revision = "4b37ea22d5a1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        "special_supply_results_public_sale_details_id_region_key",
        "special_supply_results",
        ["public_sale_details_id", "region"],
    )


def downgrade():
    op.drop_constraint(
        "special_supply_results_public_sale_details_id_region_key",
        "special_supply_results",
        type_="unique",
    )
