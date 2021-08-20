"""alter_post_attachments_table

Revision ID: d14976f052ab
Revises: 613eae109801
Create Date: 2021-08-19 12:21:30.831613

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

revision = "d14976f052ab"
down_revision = "613eae109801"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "post_attachments_post_id_key", "post_attachments", type_="unique"
    )
    op.add_column(
        "posts",
        sa.Column(
            "contents_num", sa.SmallInteger(), nullable=False, server_default=text("0")
        ),
    )


def downgrade():
    op.drop_column("posts", "contents_num")
    op.create_unique_constraint(
        "post_attachments_post_id_key", "post_attachments", ["post_id"]
    )
