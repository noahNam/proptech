"""create_post_attachments_table

Revision ID: 2a42714fc40f
Revises: 072ad674bd49
Create Date: 2021-08-04 15:33:27.659113

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '2a42714fc40f'
down_revision = '072ad674bd49'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('post_attachments',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('post_id', sa.BigInteger(), nullable=False),
                    sa.Column('type', sa.SmallInteger(), nullable=False),
                    sa.Column('file_name', sa.String(length=50), nullable=False),
                    sa.Column('path', sa.String(length=150), nullable=False),
                    sa.Column('extension', sa.String(length=4), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('post_id')
                    )


def downgrade():
    op.drop_table('post_attachments')
