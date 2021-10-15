"""alter_private_sale_avg_price_table

Revision ID: 90a817a21293
Revises: 8241c39d8164
Create Date: 2021-10-15 16:20:07.886139

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '90a817a21293'
down_revision = '8241c39d8164'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('private_sale_avg_prices', sa.Column('trade_status', sa.SmallInteger(), nullable=False, server_default="0"))
    op.add_column('private_sale_avg_prices', sa.Column('deposit_status', sa.SmallInteger(), nullable=False, server_default="0"))


def downgrade():
    op.drop_column('private_sale_avg_prices', 'deposit_status')
    op.drop_column('private_sale_avg_prices', 'trade_status')
