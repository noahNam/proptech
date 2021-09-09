"""create user_analysis_categories table

Revision ID: c9f10bd80f57
Revises: 657f05d6c187
Create Date: 2021-08-27 21:53:24.616267

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "c9f10bd80f57"
down_revision = "657f05d6c187"
branch_labels = None
depends_on = None


def upgrade():

    # user_analysis_categories 테이블 생성
    op.create_table(
        "user_analysis_categories",
        sa.Column(
            "id", sa.SmallInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("div", sa.String(length=1), nullable=False),
        sa.Column("category", sa.SmallInteger(), nullable=False),
        sa.Column("title", sa.String(length=20), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # user_analysis_category_details 테이블 생성
    op.create_table(
        "user_analysis_category_details",
        sa.Column(
            "id", sa.SmallInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("user_analysis_category_id", sa.SmallInteger(), nullable=False),
        sa.Column("format_text", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_analysis_category_id"], ["user_analysis_categories.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # user_analysis.div 컬럼 추가
    op.add_column(
        "user_analysis", sa.Column("div", sa.String(length=1), nullable=False)
    )

    # private_sales, private_sale_details index 추가
    op.create_index(
        op.f("ix_private_sale_details_trade_type"),
        "private_sale_details",
        ["trade_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_private_sales_building_type"),
        "private_sales",
        ["building_type"],
        unique=False,
    )


def downgrade():
    op.drop_column("user_analysis", "div")
    op.drop_index(
        op.f("ix_private_sale_details_trade_type"), table_name="private_sale_details"
    )
    op.drop_index(op.f("ix_private_sales_building_type"), table_name="private_sales")
    op.drop_table("user_analysis_category_details")
    op.drop_table("user_analysis_categories")
    # ### end Alembic commands ###
