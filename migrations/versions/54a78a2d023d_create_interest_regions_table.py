"""create interest_regions table

Revision ID: 54a78a2d023d
Revises: b3ae031c393f
Create Date: 2021-06-28 14:59:07.772860

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '54a78a2d023d'
down_revision = 'b3ae031c393f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('interest_regions',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True,
                              nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('region_id', sa.SmallInteger(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('user_id')
                    )


def downgrade():
    op.drop_table('interest_regions')
