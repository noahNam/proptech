"""create app_agree_terms table

Revision ID: 88efa8e1b8c5
Revises: 80f2d6eebad0
Create Date: 2021-06-16 10:40:14.915473

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "88efa8e1b8c5"
down_revision = "80f2d6eebad0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "app_agree_terms",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("private_user_info_yn", sa.Boolean(), nullable=False),
        sa.Column("required_terms_yn", sa.Boolean(), nullable=False),
        sa.Column("receipt_marketing_yn", sa.Boolean(), nullable=False),
        sa.Column("receipt_marketing_date", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_app_agree_terms_user_id"), "app_agree_terms", ["user_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_app_agree_terms_user_id"), table_name="app_agree_terms")
    op.drop_table("app_agree_terms")
