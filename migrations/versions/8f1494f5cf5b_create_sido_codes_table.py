"""create sido_codes table

Revision ID: 8f1494f5cf5b
Revises: e4a3c0dae264
Create Date: 2021-06-30 00:07:41.244282

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8f1494f5cf5b'
down_revision = 'e4a3c0dae264'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('sido_codes',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('sido_code', sa.Integer(), nullable=False),
                    sa.Column('sido_name', sa.String(length=10), nullable=False),
                    sa.Column('sigugun_code', sa.Integer(), nullable=False),
                    sa.Column('sigugun_name', sa.String(length=10), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )

    with open("./migrations/seeds/sido_codes.sql") as fp:
        op.execute(fp.read())


def downgrade():
    op.drop_table('sido_codes')
