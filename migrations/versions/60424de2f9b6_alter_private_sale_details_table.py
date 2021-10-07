"""alter private_sale_details_table

Revision ID: 60424de2f9b6
Revises: faaba582fc02
Create Date: 2021-09-27 15:17:57.902370

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "60424de2f9b6"
down_revision = "faaba582fc02"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "private_sale_details", sa.Column("contract_ym", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_private_sale_details_contract_ym"),
        "private_sale_details",
        ["contract_ym"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_private_sale_details_contract_ym"), table_name="private_sale_details"
    )
    op.drop_column("private_sale_details", "contract_ym")
