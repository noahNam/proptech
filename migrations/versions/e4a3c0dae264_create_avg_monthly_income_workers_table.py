"""create avg_monthly_income_workers table

Revision ID: e4a3c0dae264
Revises: 407554a1fdaf
Create Date: 2021-06-29 19:06:11.528850

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e4a3c0dae264'
down_revision = '407554a1fdaf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('avg_monthly_income_workers',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('year', sa.String(length=4), nullable=False),
                    sa.Column('three', sa.Integer(), nullable=False),
                    sa.Column('four', sa.Integer(), nullable=False),
                    sa.Column('five', sa.Integer(), nullable=False),
                    sa.Column('six', sa.Integer(), nullable=False),
                    sa.Column('seven', sa.Integer(), nullable=False),
                    sa.Column('eight', sa.Integer(), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('avg_monthly_income_workers')
