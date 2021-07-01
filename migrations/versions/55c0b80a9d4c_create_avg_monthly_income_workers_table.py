"""create avg_monthly_income_workers table

Revision ID: 55c0b80a9d4c
Revises: adb1abcd2216
Create Date: 2021-07-01 23:22:51.569990

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '55c0b80a9d4c'
down_revision = 'adb1abcd2216'
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
