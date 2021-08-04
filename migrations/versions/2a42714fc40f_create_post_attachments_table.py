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
    op.add_column('posts', sa.Column('category_detail_id', sa.SmallInteger(), nullable=False))
    op.add_column('posts', sa.Column('desc', sa.String(length=200), nullable=False))
    op.create_index(op.f('ix_posts_category_detail_id'), 'posts', ['category_detail_id'], unique=False)
    op.drop_constraint('posts_user_id_fkey', 'posts', type_='foreignkey')
    op.drop_column('posts', 'user_id')
    op.drop_column('posts', 'type')
    op.drop_column('posts', 'last_admin_action_at')
    op.drop_column('posts', 'last_admin_action')


def downgrade():
    op.add_column('posts', sa.Column('last_admin_action', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('posts',
                  sa.Column('last_admin_action_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('posts', sa.Column('type', sa.VARCHAR(length=10), autoincrement=False, nullable=False))
    op.add_column('posts', sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=False))
    op.create_foreign_key('posts_user_id_fkey', 'posts', 'users', ['user_id'], ['id'])
    op.drop_index(op.f('ix_posts_category_detail_id'), table_name='posts')
    op.drop_column('posts', 'desc')
    op.drop_column('posts', 'category_detail_id')
    op.drop_table('post_attachments')
