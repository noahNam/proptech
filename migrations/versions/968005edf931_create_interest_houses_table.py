"""create interest_houses table

Revision ID: 968005edf931
Revises: 345108bbb3a0
Create Date: 2021-07-06 13:14:08.874065

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '968005edf931'
down_revision = '345108bbb3a0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('interest_houses',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('ref_id', sa.BigInteger(), nullable=False),
                    sa.Column('type', sa.SmallInteger(), nullable=False),
                    sa.Column('is_like', sa.Boolean(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('user_id', 'ref_id', 'type')
                    )
    op.create_index(op.f('ix_interest_houses_ref_id'), 'interest_houses', ['ref_id'], unique=False)
    op.create_index(op.f('ix_interest_houses_user_id'), 'interest_houses', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_interest_houses_user_id'), table_name='interest_houses')
    op.drop_index(op.f('ix_interest_houses_ref_id'), table_name='interest_houses')
    op.drop_table('interest_houses')
