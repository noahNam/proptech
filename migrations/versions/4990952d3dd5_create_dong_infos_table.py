"""create dong_infos table

Revision ID: 4990952d3dd5
Revises: e6780badc04a
Create Date: 2021-09-09 18:03:31.142444

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4990952d3dd5'
down_revision = 'e6780badc04a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('dong_infos',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('private_sales_id', sa.BigInteger(), nullable=False),
                    sa.Column('dong', sa.String(length=10), nullable=True),
                    sa.Column('floor', sa.SmallInteger(), nullable=True),
                    sa.Column('structure_type', sa.String(length=3), nullable=True),
                    sa.ForeignKeyConstraint(['private_sales_id'], ['private_sales.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('room_infos',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
                    sa.Column('dong_info_id', sa.BigInteger(), nullable=False),
                    sa.Column('area_type', sa.String(length=5), nullable=True),
                    sa.Column('private_area', sa.Float(), nullable=True),
                    sa.Column('supply_area', sa.Float(), nullable=True),
                    sa.Column('registration_tax', sa.SmallInteger(), nullable=True),
                    sa.Column('holding_tax', sa.SmallInteger(), nullable=True),
                    sa.Column('multi_house_tax', sa.SmallInteger(), nullable=True),
                    sa.Column('changing_tax', sa.SmallInteger(), nullable=True),
                    sa.Column('winter_administration_cost', sa.SmallInteger(), nullable=True),
                    sa.Column('summer_administration_cost', sa.SmallInteger(), nullable=True),
                    sa.ForeignKeyConstraint(['dong_info_id'], ['dong_infos.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('room_photos',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True,
                              nullable=False),
                    sa.Column('room_info_id', sa.BigInteger(), nullable=False),
                    sa.Column('type', sa.String(length=3), nullable=False),
                    sa.Column('file_name', sa.String(length=20), nullable=False),
                    sa.Column('path', sa.String(length=150), nullable=False),
                    sa.Column('extension', sa.String(length=4), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['room_info_id'], ['room_infos.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('room_info_id')
                    )

    op.add_column('private_sales', sa.Column('supply_household', sa.SmallInteger(), nullable=True))
    op.add_column('private_sales', sa.Column('move_in_year', sa.String(length=8), nullable=True))
    op.add_column('private_sales', sa.Column('construct_company', sa.String(length=30), nullable=True))
    op.add_column('private_sales', sa.Column('dong_num', sa.SmallInteger(), nullable=True))
    op.add_column('private_sales', sa.Column('park_space_num', sa.Float(), nullable=True))
    op.add_column('private_sales', sa.Column('heating_type', sa.String(length=10), nullable=True))
    op.add_column('private_sales', sa.Column('floor_area_ratio', sa.SmallInteger(), nullable=True))
    op.add_column('private_sales', sa.Column('building_cover_ratio', sa.SmallInteger(), nullable=True))


def downgrade():
    op.drop_column('private_sales', 'building_cover_ratio')
    op.drop_column('private_sales', 'floor_area_ratio')
    op.drop_column('private_sales', 'heating_type')
    op.drop_column('private_sales', 'park_space_num')
    op.drop_column('private_sales', 'dong_num')
    op.drop_column('private_sales', 'construct_company')
    op.drop_column('private_sales', 'move_in_year')
    op.drop_column('private_sales', 'supply_household')

    op.drop_table('room_photos')
    op.drop_table('room_infos')
    op.drop_table('dong_infos')
