"""alter_post_attachments_table

Revision ID: ce662f424c56
Revises: 613eae109801
Create Date: 2021-08-18 17:01:03.517890

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'ce662f424c56'
down_revision = '613eae109801'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('post_attachments_post_id_key', 'post_attachments', type_='unique')


def downgrade():
    op.create_unique_constraint('post_attachments_post_id_key', 'post_attachments', ['post_id'])
