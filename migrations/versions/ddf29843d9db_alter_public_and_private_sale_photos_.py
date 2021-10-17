"""alter_public_and_private_sale_photos_table

Revision ID: ddf29843d9db
Revises: 3588a240ffa2
Create Date: 2021-10-13 01:43:36.998356

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "ddf29843d9db"
down_revision = "3588a240ffa2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "private_sale_photos",
        sa.Column("is_thumbnail", sa.Boolean(), nullable=False, server_default="False"),
    )
    op.add_column(
        "private_sale_photos",
        sa.Column(
            "seq",
            sa.SmallInteger(),
            autoincrement=True,
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "public_sale_photos",
        sa.Column("is_thumbnail", sa.Boolean(), nullable=False, server_default="False"),
    )
    op.add_column(
        "public_sale_photos",
        sa.Column(
            "seq",
            sa.SmallInteger(),
            autoincrement=True,
            nullable=False,
            server_default="0",
        ),
    )


def downgrade():
    op.drop_column("public_sale_photos", "seq")
    op.drop_column("public_sale_photos", "is_thumbnail")
    op.drop_column("private_sale_photos", "seq")
    op.drop_column("private_sale_photos", "is_thumbnail")
