"""create sido_codes table

Revision ID: 5b9c5f3e68d4
Revises: 8a5708d11640
Create Date: 2021-07-07 19:43:18.819111

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5b9c5f3e68d4'
down_revision = '8a5708d11640'
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
