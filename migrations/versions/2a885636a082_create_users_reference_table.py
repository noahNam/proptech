"""create users_reference table

Revision ID: 2a885636a082
Revises: 
Create Date: 2021-07-07 19:39:09.094880

"""
from alembic import op
import sqlalchemy as sa

revision = "2a885636a082"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
            autoincrement=False,
        ),
        sa.Column("email", sa.String(length=75), nullable=True),
        sa.Column("is_required_agree_terms", sa.Boolean(), nullable=False),
        sa.Column("join_date", sa.String(length=8), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_out", sa.Boolean(), nullable=False),
        sa.Column("number_ticket", sa.SmallInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "devices",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("os", sa.String(length=3), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_auth", sa.Boolean(), nullable=False),
        sa.Column("phone_number", sa.String(length=11), nullable=True),
        sa.Column("endpoint", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "receive_push_types",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("is_official", sa.Boolean(), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False),
        sa.Column("is_marketing", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "user_profiles",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("nickname", sa.String(length=12), nullable=True),
        sa.Column("last_update_code", sa.SmallInteger(), nullable=True),
        sa.Column("survey_step", sa.SmallInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "device_tokens",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("device_id", sa.BigInteger(), nullable=False),
        sa.Column("token", sa.String(length=163), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"],),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id"),
    )

    op.create_table(
        "user_infos",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("user_profile_id", sa.BigInteger(), nullable=False),
        sa.Column("code", sa.SmallInteger(), nullable=True),
        sa.Column("value", sa.String(length=12), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_profile_id"], ["user_profiles.id"],),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_profile_id", "code"),
    )

    op.create_table(
        "interest_houses",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("house_id", sa.BigInteger(), nullable=False),
        sa.Column("type", sa.SmallInteger(), nullable=False),
        sa.Column("is_like", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "house_id", "type"),
    )
    op.create_index(
        op.f("ix_interest_houses_house_id"),
        "interest_houses",
        ["house_id"],
        unique=False,
    )

    op.create_table(
        "tickets",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("type", sa.SmallInteger(), nullable=False),
        sa.Column("amount", sa.SmallInteger(), nullable=False),
        sa.Column("sign", sa.String(length=5), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.String(length=6), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "ticket_targets",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("ticket_id", sa.BigInteger(), nullable=False),
        sa.Column("public_house_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"],),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("user_infos")
    op.drop_table("device_tokens")
    op.drop_table("user_profiles")
    op.drop_table("receive_push_types")
    op.drop_table("devices")
    op.drop_index(op.f("ix_interest_houses_house_id"), table_name="interest_houses")
    op.drop_table("interest_houses")
    op.drop_table("ticket_targets")
    op.drop_table("tickets")
    op.drop_table("users")
