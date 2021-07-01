"""create notifications table

Revision ID: 407554a1fdaf
Revises: adb1abcd2216
Create Date: 2021-06-28 16:10:29.516221

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '407554a1fdaf'
down_revision = 'adb1abcd2216'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('notifications',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('token', sa.String(length=163), nullable=False),
                    sa.Column('endpoint', sa.String(length=100), nullable=True),
                    sa.Column('topic', sa.String(length=6), nullable=False),
                    sa.Column('badge_type', sa.String(length=3), nullable=False),
                    sa.Column('message', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
                              nullable=False),
                    sa.Column('is_read', sa.Boolean(), nullable=False),
                    sa.Column('is_pending', sa.Boolean(), nullable=False),
                    sa.Column('status', sa.SmallInteger(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('notifications')
