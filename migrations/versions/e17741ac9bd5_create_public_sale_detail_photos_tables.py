"""create_public_sale_detail_photos_tables

Revision ID: e17741ac9bd5
Revises: 65261925d8fa
Create Date: 2021-07-15 13:39:16.990510

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e17741ac9bd5'
down_revision = '65261925d8fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('public_sale_detail_photos',
                    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True,
                              nullable=False),
                    sa.Column('public_sale_details_id', sa.BigInteger(), nullable=False),
                    sa.Column('file_name', sa.String(length=20), nullable=False),
                    sa.Column('path', sa.String(length=150), nullable=False),
                    sa.Column('extension', sa.String(length=4), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['public_sale_details_id'], ['public_sale_details.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('public_sale_details_id')
                    )
    op.drop_column('devices', 'endpoint')
    op.drop_index('ix_interest_houses_user_id', table_name='interest_houses')
    op.create_foreign_key(None, 'interest_houses', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'interest_houses', type_='foreignkey')
    op.create_index('ix_interest_houses_user_id', 'interest_houses', ['user_id'], unique=False)
    op.add_column('devices',
                  sa.Column('endpoint', sa.VARCHAR(length=100), server_default=sa.text('NULL::character varying'),
                            autoincrement=False, nullable=True))
    op.drop_table('public_sale_detail_photos')
    # ### end Alembic commands ###
