"""create notice_template table

Revision ID: 94f60319ebfc
Revises: 4990952d3dd5
Create Date: 2021-09-12 17:15:38.843213

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '94f60319ebfc'
down_revision = '4990952d3dd5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('notice_templates',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('title', sa.String(length=100), nullable=False),
                    sa.Column('content', sa.String(length=200), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('notice_templates')
