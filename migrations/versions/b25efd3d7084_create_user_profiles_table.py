"""create user_profiles table

Revision ID: b25efd3d7084
Revises: d5456e9c2f9e
Create Date: 2021-06-28 15:37:27.396590

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b25efd3d7084'
down_revision = 'd5456e9c2f9e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user_profiles',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('nickname', sa.String(length=12), nullable=True),
                    sa.Column('last_update_code', sa.SmallInteger(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('user_id')
                    )


def downgrade():
    op.drop_table('user_profiles')
