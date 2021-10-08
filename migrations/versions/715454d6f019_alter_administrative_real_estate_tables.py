"""alter_administrative_real_estate_tables

Revision ID: 715454d6f019
Revises: 60424de2f9b6
Create Date: 2021-10-06 01:26:33.648180

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "715454d6f019"
down_revision = "60424de2f9b6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "administrative_divisions",
        sa.Column("apt_trade_price", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "administrative_divisions",
        sa.Column(
            "apt_deposit_price", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "administrative_divisions",
        sa.Column("op_trade_price", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "administrative_divisions",
        sa.Column("op_deposit_price", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "administrative_divisions",
        sa.Column("front_legal_code", sa.String(length=5), nullable=False),
    )
    op.add_column(
        "administrative_divisions",
        sa.Column("back_legal_code", sa.String(length=5), nullable=False),
    )
    op.create_index(
        op.f("ix_administrative_divisions_back_legal_code"),
        "administrative_divisions",
        ["back_legal_code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_administrative_divisions_front_legal_code"),
        "administrative_divisions",
        ["front_legal_code"],
        unique=False,
    )
    op.drop_column("administrative_divisions", "real_deposit_price")
    op.drop_column("administrative_divisions", "real_rent_price")
    op.drop_column("administrative_divisions", "real_trade_price")
    op.add_column(
        "real_estates",
        sa.Column(
            "front_legal_code",
            sa.String(length=5),
            nullable=False,
            server_default="00000",
        ),
    )
    op.add_column(
        "real_estates",
        sa.Column(
            "back_legal_code",
            sa.String(length=5),
            nullable=False,
            server_default="00000",
        ),
    )
    op.create_index(
        op.f("ix_real_estates_back_legal_code"),
        "real_estates",
        ["back_legal_code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_real_estates_front_legal_code"),
        "real_estates",
        ["front_legal_code"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_real_estates_front_legal_code"), table_name="real_estates")
    op.drop_index(op.f("ix_real_estates_back_legal_code"), table_name="real_estates")
    op.drop_column("real_estates", "back_legal_code")
    op.drop_column("real_estates", "front_legal_code")
    op.add_column(
        "administrative_divisions",
        sa.Column(
            "real_trade_price", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "administrative_divisions",
        sa.Column("real_rent_price", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "administrative_divisions",
        sa.Column(
            "real_deposit_price", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.drop_index(
        op.f("ix_administrative_divisions_front_legal_code"),
        table_name="administrative_divisions",
    )
    op.drop_index(
        op.f("ix_administrative_divisions_back_legal_code"),
        table_name="administrative_divisions",
    )
    op.drop_column("administrative_divisions", "back_legal_code")
    op.drop_column("administrative_divisions", "front_legal_code")
    op.drop_column("administrative_divisions", "op_deposit_price")
    op.drop_column("administrative_divisions", "op_trade_price")
    op.drop_column("administrative_divisions", "apt_deposit_price")
    op.drop_column("administrative_divisions", "apt_trade_price")
