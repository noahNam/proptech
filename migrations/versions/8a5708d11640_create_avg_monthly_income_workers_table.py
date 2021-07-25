"""create avg_monthly_income_worker table

Revision ID: 8a5708d11640
Revises: 2429fc376356
Create Date: 2021-07-07 19:42:41.489960

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8a5708d11640"
down_revision = "2429fc376356"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "avg_monthly_income_workers",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("year", sa.String(length=4), nullable=False),
        sa.Column("three", sa.Integer(), nullable=False),
        sa.Column("four", sa.Integer(), nullable=False),
        sa.Column("five", sa.Integer(), nullable=False),
        sa.Column("six", sa.Integer(), nullable=False),
        sa.Column("seven", sa.Integer(), nullable=False),
        sa.Column("eight", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("avg_monthly_income_workers")
