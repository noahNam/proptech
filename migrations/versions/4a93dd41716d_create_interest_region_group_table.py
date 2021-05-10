"""create interest_region_group table

Revision ID: 4a93dd41716d
Revises: ddb9bd427bf2
Create Date: 2021-04-30 23:21:52.379274

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "4a93dd41716d"
down_revision = "ddb9bd427bf2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "interest_region_groups",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("interest_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("interest_region_groups")
