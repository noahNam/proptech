"""alter survey_results table

Revision ID: 3453a0306302
Revises: d14976f052ab
Create Date: 2021-08-20 17:40:20.890521

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "3453a0306302"
down_revision = "d14976f052ab"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "survey_results",
        sa.Column("public_newly_married_div", sa.String(length=2), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("public_first_life_div", sa.String(length=2), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("private_newly_married_div", sa.String(length=2), nullable=True),
    )
    op.add_column(
        "survey_results",
        sa.Column("private_first_life_div", sa.String(length=2), nullable=True),
    )


def downgrade():
    op.drop_column("survey_results", "private_first_life_div")
    op.drop_column("survey_results", "private_newly_married_div")
    op.drop_column("survey_results", "public_first_life_div")
    op.drop_column("survey_results", "public_newly_married_div")
