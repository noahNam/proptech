"""create receive_push_type_histories table

Revision ID: dd08a0fabc3c
Revises: 5b9c5f3e68d4
Create Date: 2021-07-07 19:44:33.247844

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'dd08a0fabc3c'
down_revision = '5b9c5f3e68d4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('receive_push_type_histories',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True,
                              nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('push_type', sa.String(length=9), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('receive_push_type_histories')
