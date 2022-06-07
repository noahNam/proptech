"""remove cascade option

Revision ID: c8dc095374f5
Revises: b03bd64d11c8
Create Date: 2021-11-17 11:13:05.414393

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "c8dc095374f5"
down_revision = "b03bd64d11c8"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "dong_infos_private_sale_id_fkey", "dong_infos", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "dong_infos", "private_sales", ["private_sale_id"], ["id"]
    )

    op.drop_constraint(
        "general_supply_results_public_sale_detail_id_fkey",
        "general_supply_results",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "general_supply_results",
        "public_sale_details",
        ["public_sale_detail_id"],
        ["id"],
    )

    op.drop_constraint(
        "private_sale_details_private_sale_id_fkey",
        "private_sale_details",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None, "private_sale_details", "private_sales", ["private_sale_id"], ["id"]
    )

    op.drop_constraint(
        "private_sale_photos_private_sale_id_fkey",
        "private_sale_photos",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None, "private_sale_photos", "private_sales", ["private_sale_id"], ["id"]
    )

    op.drop_constraint(
        "private_sales_real_estate_id_fkey", "private_sales", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "private_sales", "real_estates", ["real_estate_id"], ["id"]
    )

    op.drop_constraint(
        "public_sale_detail_photos_public_sale_detail_id_key",
        "public_sale_detail_photos",
        type_="unique",
    )
    op.drop_constraint(
        "public_sale_detail_photos_public_sale_detail_id_fkey",
        "public_sale_detail_photos",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "public_sale_detail_photos",
        "public_sale_details",
        ["public_sale_detail_id"],
        ["id"],
    )

    op.drop_constraint(
        "public_sale_details_public_sale_id_fkey",
        "public_sale_details",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None, "public_sale_details", "public_sales", ["public_sale_id"], ["id"]
    )

    op.drop_constraint(
        "public_sale_photos_public_sale_id_fkey",
        "public_sale_photos",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None, "public_sale_photos", "public_sales", ["public_sale_id"], ["id"]
    )

    op.drop_constraint(
        "public_sales_real_estate_id_fkey", "public_sales", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "public_sales", "real_estates", ["real_estate_id"], ["id"]
    )

    op.drop_constraint("room_infos_dong_info_id_fkey", "room_infos", type_="foreignkey")
    op.create_foreign_key(None, "room_infos", "dong_infos", ["dong_info_id"], ["id"])

    op.drop_constraint(
        "room_photos_room_info_id_fkey", "room_photos", type_="foreignkey"
    )
    op.create_foreign_key(None, "room_photos", "room_infos", ["room_info_id"], ["id"])

    op.drop_constraint(
        "special_supply_results_public_sale_detail_id_fkey",
        "special_supply_results",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "special_supply_results",
        "public_sale_details",
        ["public_sale_detail_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(None, "special_supply_results", type_="foreignkey")
    op.create_foreign_key(
        "special_supply_results_public_sale_detail_id_fkey",
        "special_supply_results",
        "public_sale_details",
        ["public_sale_detail_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(None, "room_photos", type_="foreignkey")
    op.create_foreign_key(
        "room_photos_room_info_id_fkey",
        "room_photos",
        "room_infos",
        ["room_info_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(None, "room_infos", type_="foreignkey")
    op.create_foreign_key(
        "room_infos_dong_info_id_fkey",
        "room_infos",
        "dong_infos",
        ["dong_info_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(None, "public_sales", type_="foreignkey")
    op.create_foreign_key(
        "public_sales_real_estate_id_fkey",
        "public_sales",
        "real_estates",
        ["real_estate_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(None, "public_sale_photos", type_="foreignkey")
    op.create_foreign_key(
        "public_sale_photos_public_sale_id_fkey",
        "public_sale_photos",
        "public_sales",
        ["public_sale_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(None, "public_sale_details", type_="foreignkey")
    op.create_foreign_key(
        "public_sale_details_public_sale_id_fkey",
        "public_sale_details",
        "public_sales",
        ["public_sale_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(None, "public_sale_detail_photos", type_="foreignkey")
    op.create_foreign_key(
        "public_sale_detail_photos_public_sale_detail_id_fkey",
        "public_sale_detail_photos",
        "public_sale_details",
        ["public_sale_detail_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "public_sale_detail_photos_public_sale_detail_id_key",
        "public_sale_detail_photos",
        ["public_sale_detail_id"],
    )

    op.drop_constraint(None, "private_sales", type_="foreignkey")
    op.create_foreign_key(
        "private_sales_real_estate_id_fkey",
        "private_sales",
        "real_estates",
        ["real_estate_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(None, "private_sale_photos", type_="foreignkey")
    op.create_foreign_key(
        "private_sale_photos_private_sale_id_fkey",
        "private_sale_photos",
        "private_sales",
        ["private_sale_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(None, "private_sale_details", type_="foreignkey")
    op.create_foreign_key(
        "private_sale_details_private_sale_id_fkey",
        "private_sale_details",
        "private_sales",
        ["private_sale_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(None, "general_supply_results", type_="foreignkey")
    op.create_foreign_key(
        "general_supply_results_public_sale_detail_id_fkey",
        "general_supply_results",
        "public_sale_details",
        ["public_sale_detail_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(None, "dong_infos", type_="foreignkey")
    op.create_foreign_key(
        "dong_infos_private_sale_id_fkey",
        "dong_infos",
        "private_sales",
        ["private_sale_id"],
        ["id"],
        ondelete="CASCADE",
    )
