"""alter tables_until_mvp_2

Revision ID: e6780badc04a
Revises: c9f10bd80f57
Create Date: 2021-08-31 15:17:11.694499

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e6780badc04a"
down_revision = "c9f10bd80f57"
branch_labels = None
depends_on = None


def upgrade():
    # add survey_results column
    op.add_column(
        "survey_results",
        sa.Column("public_married_income_point", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("public_married_child_point", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("public_married_address_point", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("public_married_bank_point", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("public_married_date_point", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("private_married_child_num", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("private_married_rank", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("hope_one_income_point", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("hope_one_address_point", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("hope_one_bank_point", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("hope_two_child_point", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("hope_two_household_point", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("hope_two_address_point", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("hope_two_bank_point", sa.SmallInteger(), nullable=True),
    )

    # add user_analysis_category column
    op.add_column(
        "user_analysis_categories",
        sa.Column("title", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "user_analysis_categories",
        sa.Column("seq", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "user_analysis_categories",
        sa.Column("type", sa.String(length=1), nullable=True),
    )
    op.add_column(
        "user_analysis_categories",
        sa.Column("is_active", sa.Boolean(), nullable=True),
    )


def downgrade():
    op.drop_column("user_analysis_categories", "title")
    op.drop_column("user_analysis_categories", "seq")
    op.drop_column("user_analysis_categories", "type")
    op.drop_column("user_analysis_categories", "is_active")

    op.drop_column("survey_results", "hope_two_bank_point")
    op.drop_column("survey_results", "hope_two_address_point")
    op.drop_column("survey_results", "hope_two_household_point")
    op.drop_column("survey_results", "hope_two_child_point")
    op.drop_column("survey_results", "hope_one_bank_point")
    op.drop_column("survey_results", "hope_one_address_point")
    op.drop_column("survey_results", "hope_one_income_point")
    op.drop_column("survey_results", "private_married_rank")
    op.drop_column("survey_results", "private_married_child_num")
    op.drop_column("survey_results", "public_married_date_point")
    op.drop_column("survey_results", "public_married_bank_point")
    op.drop_column("survey_results", "public_married_address_point")
    op.drop_column("survey_results", "public_married_child_point")
    op.drop_column("survey_results", "public_married_income_point")
