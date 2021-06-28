"""create devices table

Revision ID: 2cff74135ac1
Revises: e76efb1f0f73
Create Date: 2021-06-28 15:00:42.641414

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2cff74135ac1'
down_revision = 'e76efb1f0f73'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('devices',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('uuid', sa.String(length=36), nullable=False),
                    sa.Column('os', sa.String(length=3), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('is_auth', sa.Boolean(), nullable=False),
                    sa.Column('phone_number', sa.String(length=11), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('user_id')
                    )


def downgrade():
    op.drop_table('devices')
