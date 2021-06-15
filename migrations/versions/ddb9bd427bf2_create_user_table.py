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
        "users",
        sa.Column(
            "id", sa.BigInteger(), nullable=False
        ),
        sa.Column("is_home_owner", sa.Boolean(), nullable=True),
        sa.Column("interested_house_type", sa.String(length=10), nullable=True),
        sa.Column("is_required_agree_terms", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_out", sa.Boolean(), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("interest_regions")
    op.drop_table("users")
