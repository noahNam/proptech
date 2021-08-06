"""create_house_public_detail_photos

Revision ID: da750a6dd84b
Revises: 65261925d8fa
Create Date: 2021-07-16 17:39:21.489045

"""
from alembic import op
import sqlalchemy as sa

revision = "da750a6dd84b"
down_revision = "65261925d8fa"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "public_sale_detail_photos",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("public_sale_details_id", sa.BigInteger(), nullable=False),
        sa.Column("file_name", sa.String(length=20), nullable=False),
        sa.Column("path", sa.String(length=150), nullable=False),
        sa.Column("extension", sa.String(length=4), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["public_sale_details_id"], ["public_sale_details.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_sale_details_id"),
    )


def downgrade():
    op.drop_table("public_sale_detail_photos")
