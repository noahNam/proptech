"""create ticket_usage_result_reference table

Revision ID: b5d344d6d419
Revises: 3f40cf1940aa
Create Date: 2021-07-28 01:06:04.544494

"""
from alembic import op
import sqlalchemy as sa

revision = "b5d344d6d419"
down_revision = "3f40cf1940aa"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "house_type_ranks",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("ticket_usage_result_id", sa.BigInteger(), nullable=False),
        sa.Column("house_structure_type", sa.String(length=5), nullable=False),
        sa.Column("subscription_type", sa.String(length=10), nullable=False),
        sa.Column("rank", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_house_type_ranks_ticket_usage_result_id"),
        "house_type_ranks",
        ["ticket_usage_result_id"],
        unique=False,
    )
    op.create_table(
        "ticket_usage_results",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("public_house_id", sa.BigInteger(), nullable=True),
        sa.Column("ticket_id", sa.BigInteger(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ticket_usage_results_user_id"),
        "ticket_usage_results",
        ["user_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_ticket_usage_results_user_id"), table_name="ticket_usage_results"
    )
    op.drop_table("ticket_usage_results")
    op.drop_index(
        op.f("ix_house_type_ranks_ticket_usage_result_id"),
        table_name="house_type_ranks",
    )
    op.drop_table("house_type_ranks")
