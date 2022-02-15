"""create rebuild_ref_id private_sales

Revision ID: 23b09934b59e
Revises: 693088aaa4c5
Create Date: 2022-02-15 18:02:52.905961

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '23b09934b59e'
down_revision = '693088aaa4c5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('private_sales', sa.Column('rebuild_ref_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=True))


def downgrade():
    op.drop_column('private_sales', 'rebuild_ref_id')
