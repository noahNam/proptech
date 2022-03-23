"""alter private_normal_div column

Revision ID: 1342ddd4b73e
Revises: 66082c511fd4
Create Date: 2022-03-23 19:32:34.667864

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "1342ddd4b73e"
down_revision = "66082c511fd4"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "survey_results",
        "private_normal_div",
        existing_type=sa.String(length=3),
        type_=sa.String(length=10),
    )


def downgrade():
    op.alter_column(
        "survey_results",
        "private_normal_div",
        existing_type=sa.String(length=10),
        type_=sa.String(length=3),
    )
