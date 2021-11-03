"""alter_public_ref_to_private_sales_table

Revision ID: 4033f894780d
Revises: e600def058d2
Create Date: 2021-11-02 17:40:54.747730

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "4033f894780d"
down_revision = "e600def058d2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "private_sales",
        sa.Column(
            "public_ref_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("private_sales", "public_ref_id")
