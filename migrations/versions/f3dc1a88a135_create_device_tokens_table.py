"""create device_tokens table

Revision ID: f3dc1a88a135
Revises: 2cff74135ac1
Create Date: 2021-06-28 15:35:51.158214

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f3dc1a88a135'
down_revision = '2cff74135ac1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('device_tokens',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('device_id', sa.BigInteger(), nullable=False),
                    sa.Column('token', sa.String(length=163), nullable=False),
                    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('device_id')
                    )


def downgrade():
    op.drop_table('device_tokens')
