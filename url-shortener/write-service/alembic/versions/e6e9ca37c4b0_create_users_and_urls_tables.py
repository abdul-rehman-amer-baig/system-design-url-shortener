"""create users and urls tables

Revision ID: e6e9ca37c4b0
Revises:
Create Date: 2026-03-15 16:43:55.097730

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel

from alembic import op

revision: str = "e6e9ca37c4b0"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "urls",
        sa.Column(
            "short_code", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False
        ),
        sa.Column("original_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("expiration_time", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("short_code"),
    )

    op.create_index(op.f("ix_urls_user_id"), "urls", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_urls_user_id"), table_name="urls")
    op.drop_table("urls")
    op.drop_table("users")
