"""alter_index_to_all_fk_tables

Revision ID: e600def058d2
Revises: 8d1bbe4ddb4b
Create Date: 2021-11-01 06:47:02.597222

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "e600def058d2"
down_revision = "8d1bbe4ddb4b"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("articles_post_id_key", "articles", type_="unique")
    op.create_index(op.f("ix_articles_post_id"), "articles", ["post_id"], unique=True)
    op.create_index(
        op.f("ix_banner_images_banner_id"), "banner_images", ["banner_id"], unique=False
    )
    op.drop_constraint("device_tokens_device_id_key", "device_tokens", type_="unique")
    op.create_index(
        op.f("ix_device_tokens_device_id"), "device_tokens", ["device_id"], unique=True
    )
    op.create_index(
        op.f("ix_dong_infos_private_sales_id"),
        "dong_infos",
        ["private_sales_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_interest_houses_user_id"), "interest_houses", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_post_attachments_post_id"),
        "post_attachments",
        ["post_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_promotion_houses_promotion_id"),
        "promotion_houses",
        ["promotion_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_promotion_usage_counts_promotion_id"),
        "promotion_usage_counts",
        ["promotion_id"],
        unique=False,
    )
    op.drop_constraint(
        "receive_push_types_user_id_key", "receive_push_types", type_="unique"
    )
    op.create_index(
        op.f("ix_receive_push_types_user_id"),
        "receive_push_types",
        ["user_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_recently_views_user_id"), "recently_views", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_room_infos_dong_info_id"), "room_infos", ["dong_info_id"], unique=False
    )
    op.drop_constraint("room_photos_room_info_id_key", "room_photos", type_="unique")
    op.create_index(
        op.f("ix_room_photos_room_info_id"),
        "room_photos",
        ["room_info_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_special_supply_results_public_sale_details_id"),
        "special_supply_results",
        ["public_sale_details_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ticket_targets_ticket_id"),
        "ticket_targets",
        ["ticket_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_analysis_category_details_user_analysis_category_id"),
        "user_analysis_category_details",
        ["user_analysis_category_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_infos_user_profile_id"),
        "user_infos",
        ["user_profile_id"],
        unique=False,
    )
    op.drop_constraint("user_profiles_user_id_key", "user_profiles", type_="unique")
    op.create_index(
        op.f("ix_user_profiles_user_id"), "user_profiles", ["user_id"], unique=True
    )


def downgrade():
    op.drop_index(op.f("ix_user_profiles_user_id"), table_name="user_profiles")
    op.create_unique_constraint(
        "user_profiles_user_id_key", "user_profiles", ["user_id"]
    )
    op.drop_index(op.f("ix_user_infos_user_profile_id"), table_name="user_infos")
    op.drop_index(
        op.f("ix_user_analysis_category_details_user_analysis_category_id"),
        table_name="user_analysis_category_details",
    )
    op.drop_index(op.f("ix_ticket_targets_ticket_id"), table_name="ticket_targets")
    op.drop_index(
        op.f("ix_special_supply_results_public_sale_details_id"),
        table_name="special_supply_results",
    )
    op.drop_index(op.f("ix_room_photos_room_info_id"), table_name="room_photos")
    op.create_unique_constraint(
        "room_photos_room_info_id_key", "room_photos", ["room_info_id"]
    )
    op.drop_index(op.f("ix_room_infos_dong_info_id"), table_name="room_infos")
    op.drop_index(op.f("ix_recently_views_user_id"), table_name="recently_views")
    op.drop_index(
        op.f("ix_receive_push_types_user_id"), table_name="receive_push_types"
    )
    op.create_unique_constraint(
        "receive_push_types_user_id_key", "receive_push_types", ["user_id"]
    )
    op.drop_index(
        op.f("ix_promotion_usage_counts_promotion_id"),
        table_name="promotion_usage_counts",
    )
    op.drop_index(
        op.f("ix_promotion_houses_promotion_id"), table_name="promotion_houses"
    )
    op.drop_index(op.f("ix_post_attachments_post_id"), table_name="post_attachments")
    op.drop_index(op.f("ix_interest_houses_user_id"), table_name="interest_houses")
    op.drop_index(op.f("ix_dong_infos_private_sales_id"), table_name="dong_infos")
    op.drop_index(op.f("ix_device_tokens_device_id"), table_name="device_tokens")
    op.create_unique_constraint(
        "device_tokens_device_id_key", "device_tokens", ["device_id"]
    )
    op.drop_index(op.f("ix_banner_images_banner_id"), table_name="banner_images")
    op.drop_index(op.f("ix_articles_post_id"), table_name="articles")
    op.create_unique_constraint("articles_post_id_key", "articles", ["post_id"])
