"""create user_profile table
   * users table
   * user_profile_imgs table
   * interest_regions table

Revision ID: ddb9bd427bf2
Revises: 
Create Date: 2021-04-30 22:27:12.972577

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "ddb9bd427bf2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_profile_imgs",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("uuid", sa.String(length=100), nullable=True),
        sa.Column("file_name", sa.String(length=50), nullable=True),
        sa.Column("path", sa.String(length=100), nullable=True),
        sa.Column("extension", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("nickname", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=40), nullable=False),
        sa.Column("birthday", sa.String(length=8), nullable=True),
        sa.Column("gender", sa.String(length=1), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_out", sa.Boolean(), nullable=False),
        sa.Column("profile_img_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "interest_regions",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
            autoincrement=True,
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("region_id", sa.SmallInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("interest_regions")
    op.drop_table("users")
    op.drop_table("user_profile_imgs")
