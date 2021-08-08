"""create_banner_tables

Revision ID: 61505b0d4a37
Revises: f48d848b0831
Create Date: 2021-08-05 18:06:36.495946

"""
from alembic import op
import sqlalchemy as sa

revision = "61505b0d4a37"
down_revision = "f48d848b0831"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "banners",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("title", sa.String(length=50), nullable=False),
        sa.Column("desc", sa.String(length=100), nullable=True),
        sa.Column("section_type", sa.SmallInteger(), nullable=False),
        sa.Column("sub_topic", sa.SmallInteger(), nullable=False),
        sa.Column("reference_url", sa.String(length=150), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_event", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "button_links",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("title", sa.String(length=50), nullable=False),
        sa.Column("reference_url", sa.String(length=150), nullable=False),
        sa.Column("section_type", sa.SmallInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "banner_images",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("banner_id", sa.BigInteger(), nullable=False),
        sa.Column("file_name", sa.String(length=20), nullable=False),
        sa.Column("path", sa.String(length=150), nullable=False),
        sa.Column("extension", sa.String(length=4), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["banner_id"], ["banners.id"],),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("banner_images")
    op.drop_table("button_links")
    op.drop_table("banners")
