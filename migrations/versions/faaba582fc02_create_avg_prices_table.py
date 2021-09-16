"""create avg_prices table

Revision ID: faaba582fc02
Revises: 94f60319ebfc
Create Date: 2021-09-15 22:58:23.925887

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "faaba582fc02"
down_revision = "94f60319ebfc"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "private_sale_avg_prices",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("private_sales_id", sa.BigInteger(), nullable=False),
        sa.Column("pyoung", sa.SmallInteger(), nullable=False),
        sa.Column("default_pyoung", sa.SmallInteger(), nullable=False),
        sa.Column("trade_price", sa.Integer(), nullable=True),
        sa.Column("deposit_price", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_private_sale_avg_prices_private_sales_id"),
        "private_sale_avg_prices",
        ["private_sales_id"],
        unique=False,
    )

    op.create_table(
        "public_sale_avg_prices",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("public_sales_id", sa.BigInteger(), nullable=False),
        sa.Column("pyoung", sa.SmallInteger(), nullable=False),
        sa.Column("default_pyoung", sa.SmallInteger(), nullable=False),
        sa.Column("supply_price", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_public_sale_avg_prices_public_sales_id"),
        "public_sale_avg_prices",
        ["public_sales_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_public_sale_avg_prices_public_sales_id"),
        table_name="public_sale_avg_prices",
    )
    op.drop_table("public_sale_avg_prices")
    op.drop_index(
        op.f("ix_private_sale_avg_prices_private_sales_id"),
        table_name="private_sale_avg_prices",
    )
    op.drop_table("private_sale_avg_prices")
