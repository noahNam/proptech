"""create_house_tables

Revision ID: 65261925d8fa
Revises: 50659369a256
Create Date: 2021-07-13 13:02:17.205904

"""
import geoalchemy2
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '65261925d8fa'
down_revision = '50659369a256'
branch_labels = None
depends_on = None


def upgrade():
    # 로컬 사용시 postgis 주석 처리 필요
    op.execute("create extension postgis;")

    op.create_table('administrative_divisions',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True,
                              nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=False),
                    sa.Column('short_name', sa.String(length=30), nullable=False),
                    sa.Column('real_trade_price', sa.Integer(), nullable=False),
                    sa.Column('real_rent_price', sa.Integer(), nullable=False),
                    sa.Column('real_deposit_price', sa.Integer(), nullable=False),
                    sa.Column('public_sale_price', sa.Integer(), nullable=False),
                    sa.Column('level', sa.Enum('1', '2', '3', name='divisionlevelenum'), nullable=False),
                    sa.Column('coordinates',
                              geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT',
                                                         name='geometry').with_variant(sa.String(), 'sqlite'),
                              nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('real_estates',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True,
                              nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=True),
                    sa.Column('road_address', sa.String(length=100), nullable=False),
                    sa.Column('jibun_address', sa.String(length=100), nullable=False),
                    sa.Column('si_do', sa.String(length=20), nullable=False),
                    sa.Column('si_gun_gu', sa.String(length=16), nullable=False),
                    sa.Column('dong_myun', sa.String(length=16), nullable=False),
                    sa.Column('ri', sa.String(length=12), nullable=True),
                    sa.Column('road_name', sa.String(length=30), nullable=True),
                    sa.Column('road_number', sa.String(length=10), nullable=True),
                    sa.Column('land_number', sa.String(length=10), nullable=False),
                    sa.Column('is_available', sa.Boolean(), nullable=False),
                    sa.Column('coordinates',
                              geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT',
                                                         name='geometry').with_variant(sa.String(), 'sqlite'),
                              nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('private_sales',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True,
                              nullable=False),
                    sa.Column('real_estate_id', sa.BigInteger(), nullable=False),
                    sa.Column('private_area', sa.Float(), nullable=False),
                    sa.Column('supply_area', sa.Float(), nullable=False),
                    sa.Column('contract_date', sa.String(length=8), nullable=True),
                    sa.Column('deposit_price', sa.Integer(), nullable=False),
                    sa.Column('rent_price', sa.Integer(), nullable=False),
                    sa.Column('trade_price', sa.Integer(), nullable=False),
                    sa.Column('floor', sa.SmallInteger(), nullable=False),
                    sa.Column('trade_type', sa.Enum('매매', '전세', '월세', name='realtradetypeenum'), nullable=False),
                    sa.Column('building_type', sa.Enum('아파트', '오피스텔', '연립다세대', name='buildtypeenum'), nullable=False),
                    sa.Column('is_available', sa.Boolean(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['real_estate_id'], ['real_estates.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('public_sales',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True,
                              nullable=False),
                    sa.Column('real_estate_id', sa.BigInteger(), nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.Column('region', sa.String(length=20), nullable=False),
                    sa.Column('housing_category', sa.Enum('국민', '민영', name='housingcategoryenum'), nullable=False),
                    sa.Column('rent_type', sa.Enum('분양', '임대', name='renttypeenum'), nullable=False),
                    sa.Column('trade_type', sa.Enum('분양', '사전청약', name='presaletypeenum'), nullable=False),
                    sa.Column('construct_company', sa.String(length=30), nullable=True),
                    sa.Column('supply_household', sa.Integer(), nullable=False),
                    sa.Column('is_available', sa.Boolean(), nullable=False),
                    sa.Column('offer_date', sa.String(length=8), nullable=True),
                    sa.Column('subscription_start_date', sa.String(length=8), nullable=True),
                    sa.Column('subscription_end_date', sa.String(length=8), nullable=True),
                    sa.Column('special_supply_date', sa.String(length=8), nullable=True),
                    sa.Column('special_supply_etc_date', sa.String(length=8), nullable=True),
                    sa.Column('first_supply_date', sa.String(length=8), nullable=True),
                    sa.Column('first_supply_etc_date', sa.String(length=8), nullable=True),
                    sa.Column('second_supply_date', sa.String(length=8), nullable=True),
                    sa.Column('second_supply_etc_date', sa.String(length=8), nullable=True),
                    sa.Column('notice_winner_date', sa.String(length=8), nullable=True),
                    sa.Column('contract_start_date', sa.String(length=8), nullable=True),
                    sa.Column('contract_end_date', sa.String(length=8), nullable=True),
                    sa.Column('move_in_year', sa.SmallInteger(), nullable=True),
                    sa.Column('move_in_month', sa.SmallInteger(), nullable=True),
                    sa.Column('min_down_payment', sa.Integer(), nullable=False),
                    sa.Column('max_down_payment', sa.Integer(), nullable=False),
                    sa.Column('down_payment_ratio', sa.Integer(), nullable=False),
                    sa.Column('reference_url', sa.String(length=50), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['real_estate_id'], ['real_estates.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('public_sale_details',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True,
                              nullable=False),
                    sa.Column('public_sales_id', sa.BigInteger(), nullable=False),
                    sa.Column('private_area', sa.Float(), nullable=False),
                    sa.Column('supply_area', sa.Float(), nullable=False),
                    sa.Column('supply_price', sa.Integer(), nullable=False),
                    sa.Column('acquisition_tax', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['public_sales_id'], ['public_sales.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('public_sale_photos',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True,
                              nullable=False),
                    sa.Column('public_sales_id', sa.BigInteger(), nullable=False),
                    sa.Column('file_name', sa.String(length=20), nullable=False),
                    sa.Column('path', sa.String(length=150), nullable=False),
                    sa.Column('extension', sa.String(length=4), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['public_sales_id'], ['public_sales.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('public_sales_id')
                    )


def downgrade():
    op.drop_table('public_sale_photos')
    op.drop_table('public_sale_details')
    op.drop_table('public_sales')
    op.drop_table('private_sales')
    op.drop_table('real_estates')
    op.drop_table('administrative_divisions')
    op.execute("drop type renttypeenum;")
    op.execute("drop type realtradetypeenum;")
    op.execute("drop type presaletypeenum;")
    op.execute("drop type housingcategoryenum;")
    op.execute("drop type divisionlevelenum;")
    op.execute("drop type buildtypeenum;")
    op.execute("drop extension postgis;")
