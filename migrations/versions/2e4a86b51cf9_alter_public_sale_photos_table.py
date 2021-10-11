"""alter_public_sale_photos_table

Revision ID: 2e4a86b51cf9
Revises: ffb3b782c49e
Create Date: 2021-10-10 16:29:15.751936

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "2e4a86b51cf9"
down_revision = "ffb3b782c49e"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "public_sale_photos_public_sales_id_key", "public_sale_photos", type_="unique"
    )
    op.drop_index(
        "ix_public_sale_photos_public_sales_id", table_name="public_sale_photos"
    )
    op.create_index(
        op.f("ix_public_sale_photos_public_sales_id"),
        "public_sale_photos",
        ["public_sales_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_public_sale_photos_public_sales_id"), table_name="public_sale_photos"
    )
    op.create_unique_constraint(
        "public_sale_photos_public_sales_id_key",
        "public_sale_photos",
        ["public_sales_id"],
    )
    op.create_index(
        op.f("ix_public_sale_photos_public_sales_id"),
        "public_sale_photos",
        ["public_sales_id"],
        unique=True,
    )
