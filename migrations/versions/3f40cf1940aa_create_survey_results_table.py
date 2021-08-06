"""create survey_results table

Revision ID: 3f40cf1940aa
Revises: 38ad1196e6a1
Create Date: 2021-07-28 01:02:50.151519

"""
from alembic import op
import sqlalchemy as sa

revision = "3f40cf1940aa"
down_revision = "38ad1196e6a1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "survey_results",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("total_point", sa.SmallInteger(), nullable=True),
        sa.Column("detail_point_house", sa.SmallInteger(), nullable=True),
        sa.Column("detail_point_family", sa.SmallInteger(), nullable=True),
        sa.Column("detail_point_bank", sa.SmallInteger(), nullable=True),
        sa.Column("public_newly_married", sa.SmallInteger(), nullable=True),
        sa.Column("public_first_life", sa.SmallInteger(), nullable=True),
        sa.Column("public_multiple_children", sa.SmallInteger(), nullable=True),
        sa.Column("public_old_parent", sa.SmallInteger(), nullable=True),
        sa.Column("public_agency_recommend", sa.SmallInteger(), nullable=True),
        sa.Column("public_normal", sa.SmallInteger(), nullable=True),
        sa.Column("private_newly_married", sa.SmallInteger(), nullable=True),
        sa.Column("private_first_life", sa.SmallInteger(), nullable=True),
        sa.Column("private_multiple_children", sa.SmallInteger(), nullable=True),
        sa.Column("private_old_parent", sa.SmallInteger(), nullable=True),
        sa.Column("private_agency_recommend", sa.SmallInteger(), nullable=True),
        sa.Column("private_normal", sa.SmallInteger(), nullable=True),
        sa.Column("hope_town_phase_one", sa.SmallInteger(), nullable=True),
        sa.Column("hope_town_phase_two", sa.SmallInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_survey_results_user_id"), "survey_results", ["user_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_survey_results_user_id"), table_name="survey_results")
    op.drop_table("survey_results")
