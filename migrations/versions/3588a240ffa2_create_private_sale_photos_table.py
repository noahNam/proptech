"""create_private_sale_photos_table

Revision ID: 3588a240ffa2
Revises: 2e4a86b51cf9
Create Date: 2021-10-10 16:41:56.765045

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '3588a240ffa2'
down_revision = '2e4a86b51cf9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('private_sale_photos',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('private_sales_id', sa.BigInteger(), nullable=False),
    sa.Column('file_name', sa.String(length=20), nullable=False),
    sa.Column('path', sa.String(length=150), nullable=False),
    sa.Column('extension', sa.String(length=4), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['private_sales_id'], ['private_sales.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_private_sale_photos_private_sales_id'), 'private_sale_photos', ['private_sales_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_private_sale_photos_private_sales_id'), table_name='private_sale_photos')
    op.drop_table('private_sale_photos')
