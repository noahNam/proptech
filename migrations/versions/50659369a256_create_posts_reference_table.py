"""create posts_reference table

Revision ID: 50659369a256
Revises: e25e9eef6f19
Create Date: 2021-07-11 18:39:13.974717

"""
from alembic import op
import sqlalchemy as sa

revision = "50659369a256"
down_revision = "d0ec2fc73bba"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "posts",
        sa.Column(
            "id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("category_id", sa.SmallInteger(), nullable=False),
        sa.Column("category_detail_id", sa.SmallInteger(), nullable=False),
        sa.Column("title", sa.String(length=50), nullable=False),
        sa.Column("desc", sa.String(length=200), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("read_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_posts_category_id"), "posts", ["category_id"], unique=False
    )
    op.create_index(
        op.f("ix_posts_category_detail_id"),
        "posts",
        ["category_detail_id"],
        unique=False,
    )

    op.create_table(
        "articles",
        sa.Column(
            "id", sa.SmallInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("post_id", sa.BigInteger(), nullable=False),
        sa.Column("body", sa.Unicode(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"],),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("post_id"),
    )


def downgrade():
    op.drop_table("articles")
    op.drop_index(op.f("ix_posts_category_id"), table_name="posts")
    op.drop_index(op.f("ix_posts_category_detail_id"), table_name="posts")
    op.drop_table("posts")
