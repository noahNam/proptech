"""create sido_codes table

Revision ID: a7e863bcd3be
Revises: 55c0b80a9d4c
Create Date: 2021-07-01 23:24:34.418290

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a7e863bcd3be'
down_revision = '55c0b80a9d4c'
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
