"""alter survey_results table

Revision ID: 66082c511fd4
Revises: 58192dd86224
Create Date: 2022-03-17 22:03:37.193348

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '66082c511fd4'
down_revision = '58192dd86224'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('survey_results', sa.Column('public_normal_div', sa.String(length=3), nullable=True))
    op.add_column('survey_results', sa.Column('private_normal_div', sa.String(length=3), nullable=True))
    op.alter_column(
        "survey_results",
        "public_agency_recommend",
        existing_type=sa.SmallInteger(),
        type_=sa.Boolean(),
        nullable=True
    )
    op.alter_column(
        "survey_results",
        "private_agency_recommend",
        existing_type=sa.SmallInteger(),
        type_=sa.Boolean(),
        nullable=True
    )


def downgrade():
    op.drop_column('survey_results', 'private_normal_div')
    op.drop_column('survey_results', 'public_normal_div')
    op.alter_column(
        "survey_results",
        "public_agency_recommend",
        existing_type=sa.Boolean(),
        type_=sa.SmallInteger(),
    )
    op.alter_column(
        "survey_results",
        "private_agency_recommend",
        existing_type=sa.Boolean(),
        type_=sa.SmallInteger(),
    )