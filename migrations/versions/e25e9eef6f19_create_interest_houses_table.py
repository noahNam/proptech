"""create interest_houses table

Revision ID: e25e9eef6f19
Revises: d0ec2fc73bba
Create Date: 2021-07-07 20:00:10.303138

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e25e9eef6f19'
down_revision = 'd0ec2fc73bba'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('interest_houses',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('house_id', sa.BigInteger(), nullable=False),
                    sa.Column('type', sa.SmallInteger(), nullable=False),
                    sa.Column('is_like', sa.Boolean(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('user_id', 'house_id', 'type')
                    )
    op.create_index(op.f('ix_interest_houses_house_id'), 'interest_houses', ['house_id'], unique=False)
    op.create_index(op.f('ix_interest_houses_user_id'), 'interest_houses', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_interest_houses_user_id'), table_name='interest_houses')
    op.drop_index(op.f('ix_interest_houses_house_id'), table_name='interest_houses')
    op.drop_table('interest_houses')
