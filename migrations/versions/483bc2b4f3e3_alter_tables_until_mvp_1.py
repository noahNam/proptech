"""alter_tables_until_MVP

Revision ID: 657f05d6c187
Revises: 3453a0306302
Create Date: 2021-08-23 16:19:22.630168

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

revision = "657f05d6c187"
down_revision = "483bc2b4f3e3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "general_supply_results",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
            autoincrement=True,
        ),
        sa.Column("public_sale_details_id", sa.BigInteger(), nullable=False),
        sa.Column("region", sa.String(length=10), nullable=True),
        sa.Column("region_percent", sa.SmallInteger(), nullable=True),
        sa.Column("applicant_num", sa.Integer(), nullable=True),
        sa.Column("competition_rate", sa.SmallInteger(), nullable=True),
        sa.Column("win_point", sa.SmallInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["public_sale_details_id"], ["public_sale_details.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "special_supply_results",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
            autoincrement=True,
        ),
        sa.Column("public_sale_details_id", sa.BigInteger(), nullable=False),
        sa.Column("region", sa.String(length=10), nullable=True),
        sa.Column("region_percent", sa.SmallInteger(), nullable=True),
        sa.Column("multi_children_vol", sa.SmallInteger(), nullable=True),
        sa.Column("newlywed_vol", sa.SmallInteger(), nullable=True),
        sa.Column("old_parent_vol", sa.SmallInteger(), nullable=True),
        sa.Column("first_life_vol", sa.SmallInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["public_sale_details_id"], ["public_sale_details.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # alter public_sale_details
    op.add_column(
        "public_sale_details",
        sa.Column(
            "special_household",
            sa.SmallInteger(),
            nullable=False,
            server_default=text("0"),
        ),
    )
    op.add_column(
        "public_sale_details",
        sa.Column(
            "multi_children_house_hold",
            sa.SmallInteger(),
            nullable=False,
            server_default=text("0"),
        ),
    )
    op.add_column(
        "public_sale_details",
        sa.Column(
            "newlywed_house_hold",
            sa.SmallInteger(),
            nullable=False,
            server_default=text("0"),
        ),
    )
    op.add_column(
        "public_sale_details",
        sa.Column(
            "old_parent_house_hold",
            sa.SmallInteger(),
            nullable=False,
            server_default=text("0"),
        ),
    )
    op.add_column(
        "public_sale_details",
        sa.Column(
            "first_life_house_hold",
            sa.SmallInteger(),
            nullable=False,
            server_default=text("0"),
        ),
    )
    op.add_column(
        "public_sale_details",
        sa.Column(
            "general_household",
            sa.SmallInteger(),
            nullable=False,
            server_default=text("0"),
        ),
    )

    # public_sales 기타-경기 칼럼 추가
    op.add_column(
        "public_sales",
        sa.Column("special_etc_gyeonggi_date", sa.String(length=8), nullable=True),
    )
    op.add_column(
        "public_sales",
        sa.Column("first_etc_gyeonggi_date", sa.String(length=8), nullable=True),
    )
    op.add_column(
        "public_sales",
        sa.Column("second_etc_gyeonggi_date", sa.String(length=8), nullable=True),
    )


def downgrade():
    op.drop_column("public_sale_details", "general_household")
    op.drop_column("public_sale_details", "special_household")
    op.drop_column("public_sale_details", "multi_children_house_hold")
    op.drop_column("public_sale_details", "newlywed_house_hold")
    op.drop_column("public_sale_details", "old_parent_house_hold")
    op.drop_column("public_sale_details", "first_life_house_hold")
    op.drop_table("general_supply_results")
    op.drop_table("special_supply_results")
    op.drop_column("public_sales", "second_etc_gyeonggi_date")
    op.drop_column("public_sales", "first_etc_gyeonggi_date")
    op.drop_column("public_sales", "special_etc_gyeonggi_date")
