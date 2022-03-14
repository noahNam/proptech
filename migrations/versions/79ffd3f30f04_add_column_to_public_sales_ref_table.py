"""add column to public_sales table

Revision ID: 79ffd3f30f04
Revises: c020888b3733
Create Date: 2021-12-13 01:06:43.411733

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "79ffd3f30f04"
down_revision = "c020888b3733"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "public_sales", sa.Column("heating_type", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "public_sales", sa.Column("floor_area_ratio", sa.Float(), nullable=True)
    )
    op.add_column(
        "public_sales", sa.Column("building_cover_ratio", sa.Float(), nullable=True)
    )
    op.add_column(
        "public_sales", sa.Column("total_household", sa.Integer(), nullable=True)
    )
    op.add_column(
        "public_sales", sa.Column("total_park_number", sa.Integer(), nullable=True)
    )
    op.add_column(
        "public_sales", sa.Column("top_floor", sa.SmallInteger(), nullable=True)
    )
    op.add_column("public_sales", sa.Column("dong_number", sa.Integer(), nullable=True))
    op.add_column(
        "public_sales", sa.Column("contract_amount", sa.Float(), nullable=True)
    )
    op.add_column("public_sales", sa.Column("middle_amount", sa.Float(), nullable=True))
    op.add_column("public_sales", sa.Column("remain_amount", sa.Float(), nullable=True))
    op.add_column(
        "public_sales", sa.Column("sale_limit", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "public_sales",
        sa.Column("compulsory_residence", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "public_sale_details",
        sa.Column("hallway_type", sa.String(length=3), nullable=True),
    )
    op.add_column(
        "public_sale_details", sa.Column("bay", sa.SmallInteger(), nullable=True)
    )
    op.add_column(
        "public_sale_details",
        sa.Column("plate_tower_duplex", sa.String(length=3), nullable=True),
    )
    op.add_column(
        "public_sale_details",
        sa.Column("kitchen_window", sa.String(length=1), nullable=True),
    )
    op.add_column(
        "public_sale_details",
        sa.Column("cross_ventilation", sa.String(length=1), nullable=True),
    )
    op.add_column(
        "public_sale_details",
        sa.Column("alpha_room", sa.String(length=1), nullable=True),
    )
    op.add_column(
        "public_sale_details",
        sa.Column("cyber_house_link", sa.String(length=200), nullable=True),
    )


def downgrade():
    op.drop_column("public_sale_details", "cyber_house_link")
    op.drop_column("public_sale_details", "alpha_room")
    op.drop_column("public_sale_details", "cross_ventilation")
    op.drop_column("public_sale_details", "kitchen_window")
    op.drop_column("public_sale_details", "plate_tower_duplex")
    op.drop_column("public_sale_details", "bay")
    op.drop_column("public_sale_details", "hallway_type")

    op.drop_column("public_sales", "compulsory_residence")
    op.drop_column("public_sales", "sale_limit")
    op.drop_column("public_sales", "remain_amount")
    op.drop_column("public_sales", "middle_amount")
    op.drop_column("public_sales", "contract_amount")
    op.drop_column("public_sales", "dong_number")
    op.drop_column("public_sales", "top_floor")
    op.drop_column("public_sales", "total_park_number")
    op.drop_column("public_sales", "total_household")
    op.drop_column("public_sales", "building_cover_ratio")
    op.drop_column("public_sales", "floor_area_ratio")
    op.drop_column("public_sales", "heating_type")
