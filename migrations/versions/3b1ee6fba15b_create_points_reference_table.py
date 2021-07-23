"""create points_reference table

Revision ID: 3b1ee6fba15b
Revises: 65261925d8fa
Create Date: 2021-07-23 16:14:17.164229

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3b1ee6fba15b'
down_revision = '65261925d8fa'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('point_types',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('name', sa.String(length=20), nullable=False),
                    sa.Column('division', sa.String(length=7), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('points',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('type', sa.SmallInteger(), nullable=False),
                    sa.Column('amount', sa.Integer(), nullable=False),
                    sa.Column('sign', sa.String(length=5), nullable=False),
                    sa.Column('created_by', sa.String(length=6), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('points')
    op.drop_table('point_types')
