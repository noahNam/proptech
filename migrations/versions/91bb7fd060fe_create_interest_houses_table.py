"""create interest_houses table

Revision ID: 91bb7fd060fe
Revises: 345108bbb3a0
Create Date: 2021-07-06 11:02:03.168281

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '91bb7fd060fe'
down_revision = '345108bbb3a0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('interest_houses',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('ref_id', sa.BigInteger(), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_interest_houses_ref_id'), 'interest_houses', ['ref_id'], unique=False)
    op.create_index(op.f('ix_interest_houses_user_id'), 'interest_houses', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_interest_houses_user_id'), table_name='interest_houses')
    op.drop_index(op.f('ix_interest_houses_ref_id'), table_name='interest_houses')
    op.drop_table('interest_houses')
