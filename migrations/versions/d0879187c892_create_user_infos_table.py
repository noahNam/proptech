"""create user_infos table

Revision ID: d0879187c892
Revises: b25efd3d7084
Create Date: 2021-06-28 15:38:05.262437

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd0879187c892'
down_revision = 'b25efd3d7084'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user_infos',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('user_profile_id', sa.BigInteger(), nullable=False),
                    sa.Column('code', sa.SmallInteger(), nullable=True),
                    sa.Column('value', sa.String(length=8), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['user_profile_id'], ['user_profiles.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('code'),
                    sa.UniqueConstraint('user_profile_id')
                    )


def downgrade():
    op.drop_table('user_infos')
