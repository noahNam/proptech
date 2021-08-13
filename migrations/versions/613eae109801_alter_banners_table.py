"""alter_banners_table

Revision ID: 613eae109801
Revises: 61505b0d4a37
Create Date: 2021-08-13 21:09:30.269870

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

revision = '613eae109801'
down_revision = '61505b0d4a37'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('banners', sa.Column('contents_num', sa.SmallInteger(), nullable=False, server_default=text("0")))


def downgrade():
    op.drop_column('banners', 'contents_num')
