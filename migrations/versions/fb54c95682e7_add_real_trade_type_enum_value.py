"""add real_trade_type_enum value

Revision ID: fb54c95682e7
Revises: 4033f894780d
Create Date: 2021-11-05 00:56:30.482723

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fb54c95682e7'
down_revision = '4033f894780d'
branch_labels = None
depends_on = None


name = "realtradetypeenum"
tmp_name = 'tmp_' + name

# new_type = sa.Enum("매매", "전세", "월세", "분양권매매", "입주권매매", name='realtradetypeenum')
# old_type = sa.Enum("매매", "전세", "월세", name='realtradetypeenum')

old_options = ('매매', '전세', '월세')
new_options = ('매매', '전세', '월세', '분양권매매', '입주권매매')

new_type = sa.Enum(*new_options, name=name)
old_type = sa.Enum(*old_options, name=name)


def upgrade():
    op.execute('ALTER TYPE ' + name + ' RENAME TO ' + tmp_name)

    new_type.create(op.get_bind())
    op.execute('ALTER TABLE private_sale_details ALTER COLUMN trade_type ' +
               'TYPE ' + name + ' USING trade_type::text::' + name)
    op.execute('DROP TYPE ' + tmp_name)


def downgrade():
    op.execute('ALTER TYPE ' + name + ' RENAME TO ' + tmp_name)

    old_type.create(op.get_bind())
    op.execute('ALTER TABLE private_sale_details ALTER COLUMN trade_type ' +
               'TYPE ' + name + ' USING trade_type::text::' + name)
    op.execute('DROP TYPE ' + tmp_name)