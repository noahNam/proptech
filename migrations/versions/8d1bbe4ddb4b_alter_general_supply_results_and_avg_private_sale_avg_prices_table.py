"""alter_general_supply_results_and_avg_private_sale_avg_prices_table

Revision ID: 8d1bbe4ddb4b
Revises: 9aa9ab00694c
Create Date: 2021-10-26 19:25:03.754890

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "8d1bbe4ddb4b"
down_revision = "9aa9ab00694c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        op.f("ix_general_supply_results_public_sale_detail_id"),
        "general_supply_results",
        ["public_sale_detail_id"],
        unique=False,
    )
    op.create_unique_constraint(
        "general_supply_results_public_sale_detail_id_region_key",
        "general_supply_results",
        ["public_sale_detail_id", "region"],
    )

    op.add_column(
        "private_sale_avg_prices",
        sa.Column("default_trade_pyoung", sa.Float(), nullable=True),
    )
    op.add_column(
        "private_sale_avg_prices",
        sa.Column("default_deposit_pyoung", sa.Float(), nullable=True),
    )
    op.drop_column("private_sale_avg_prices", "default_pyoung")


def downgrade():
    op.add_column(
        "private_sale_avg_prices",
        sa.Column(
            "default_pyoung",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_column("private_sale_avg_prices", "default_deposit_pyoung")
    op.drop_column("private_sale_avg_prices", "default_trade_pyoung")

    op.drop_constraint(
        "general_supply_results_public_sale_detail_id_region_key",
        "general_supply_results",
        type_="unique",
    )
    op.drop_index(
        op.f("ix_general_supply_results_public_sale_detail_id"),
        table_name="general_supply_results",
    )
