"""add column private_sale_avg_prices

Revision ID: 9aa9ab00694c
Revises: 09c6c3f44ae2
Create Date: 2021-10-22 20:18:10.233114

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9aa9ab00694c'
down_revision = '09c6c3f44ae2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('private_sale_avg_prices', sa.Column('max_trade_contract_date', sa.String(length=8), nullable=True))
    op.add_column('private_sale_avg_prices', sa.Column('max_deposit_contract_date', sa.String(length=8), nullable=True))


def downgrade():
    op.drop_column('private_sale_avg_prices', 'max_deposit_contract_date')
    op.drop_column('private_sale_avg_prices', 'max_trade_contract_date')
