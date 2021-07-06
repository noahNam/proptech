"""create interest_region_groups table

Revision ID: e76efb1f0f73
Revises: 54a78a2d023d
Create Date: 2021-06-28 15:00:14.637699

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e76efb1f0f73'
down_revision = '54a78a2d023d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('interest_region_groups',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True,
                              nullable=False),
                    sa.Column('level', sa.SmallInteger(), nullable=False),
                    sa.Column('name', sa.String(length=20), nullable=False),
                    sa.Column('interest_count', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('interest_region_groups')
