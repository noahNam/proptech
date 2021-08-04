"""create recommend_codes table

Revision ID: f48d848b0831
Revises: 072ad674bd49
Create Date: 2021-08-04 16:57:59.675908

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f48d848b0831'
down_revision = '072ad674bd49'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('recommend_codes',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('code_group', sa.SmallInteger(), nullable=False),
                    sa.Column('code', sa.String(length=6), nullable=False),
                    sa.Column('code_count', sa.SmallInteger(), nullable=False),
                    sa.Column('is_used', sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_recommend_codes_user_id'), 'recommend_codes', ['user_id'], unique=False)
    op.create_index(op.f('ix_recommend_codes_code_group'), 'recommend_codes', ['code_group'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_recommend_codes_code_group'), table_name='recommend_codes')
    op.drop_index(op.f('ix_recommend_codes_user_id'), table_name='recommend_codes')
    op.drop_table('recommend_codes')
