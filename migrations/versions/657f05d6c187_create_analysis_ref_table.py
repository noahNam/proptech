"""create analysis_ref table

Revision ID: 483bc2b4f3e3
Revises: 483bc2b4f3e3
Create Date: 2021-08-24 14:57:28.711515

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "483bc2b4f3e3"
down_revision = "d14976f052ab"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "predicted_competitions",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("ticket_usage_result_id", sa.BigInteger(), nullable=False),
        sa.Column("house_structure_type", sa.String(length=10), nullable=False),
        sa.Column("region", sa.String(length=5), nullable=False),
        sa.Column("region_percentage", sa.SmallInteger(), nullable=False),
        sa.Column("multiple_children_competition", sa.SmallInteger(), nullable=True),
        sa.Column("newly_marry_competition", sa.SmallInteger(), nullable=True),
        sa.Column("old_parent_competition", sa.SmallInteger(), nullable=True),
        sa.Column("first_life_competition", sa.SmallInteger(), nullable=True),
        sa.Column("multiple_children_supply", sa.SmallInteger(), nullable=True),
        sa.Column("newly_marry_supply", sa.SmallInteger(), nullable=True),
        sa.Column("old_parent_supply", sa.SmallInteger(), nullable=True),
        sa.Column("first_life_supply", sa.SmallInteger(), nullable=True),
        sa.Column("normal_competition", sa.SmallInteger(), nullable=True),
        sa.Column("normal_supply", sa.SmallInteger(), nullable=True),
        sa.Column("normal_passing_score", sa.SmallInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_predicted_competitions_ticket_usage_result_id"),
        "predicted_competitions",
        ["ticket_usage_result_id"],
        unique=False,
    )

    op.create_table(
        "user_analysis",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("ticket_usage_result_id", sa.BigInteger(), nullable=False),
        sa.Column("div", sa.String(length=1), nullable=False),
        sa.Column("category", sa.SmallInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_analysis_ticket_usage_result_id"),
        "user_analysis",
        ["ticket_usage_result_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_user_analysis_ticket_usage_result_id"), table_name="user_analysis"
    )
    op.drop_table("user_analysis")
    op.drop_index(
        op.f("ix_predicted_competitions_ticket_usage_result_id"),
        table_name="predicted_competitions",
    )
    op.drop_table("predicted_competitions")
