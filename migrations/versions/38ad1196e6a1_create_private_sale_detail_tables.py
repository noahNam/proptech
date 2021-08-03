"""create_private_sale_detail_tables

Revision ID: 38ad1196e6a1
Revises: 2b39ceec2fb5
Create Date: 2021-07-21 22:56:30.636017

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "38ad1196e6a1"
down_revision = "2b39ceec2fb5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "private_sale_details",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("private_sales_id", sa.BigInteger(), nullable=False),
        sa.Column("private_area", sa.Float(), nullable=False),
        sa.Column("supply_area", sa.Float(), nullable=False),
        sa.Column("contract_date", sa.String(length=8), nullable=True),
        sa.Column("deposit_price", sa.Integer(), nullable=False),
        sa.Column("rent_price", sa.Integer(), nullable=False),
        sa.Column("trade_price", sa.Integer(), nullable=False),
        sa.Column("floor", sa.SmallInteger(), nullable=False),
        sa.Column(
            "trade_type",
            postgresql.ENUM(
                "매매", "전세", "월세", name="realtradetypeenum",
            ),
            nullable=False,
        ),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["private_sales_id"], ["private_sales.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # with open("./migrations/seeds/default_houses.sql") as fp:
    #     op.execute(fp.read())


def downgrade():
    op.drop_table("private_sale_details")
    op.execute("drop type realtradetypeenum;")
