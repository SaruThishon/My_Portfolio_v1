"""profile_singleton_constraint

Revision ID: c9d4e5f6a7b8
Revises: b7e3d2a1f9c8
Create Date: 2026-11-19 00:02:00.000000

Adds a unique index on a constant expression to enforce that the profile
table can only ever contain a single row. Any INSERT of a second row will
fail with a unique constraint violation at the DB level.
"""
from typing import Sequence, Union
from alembic import op

revision: str = 'c9d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b7e3d2a1f9c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # A unique index on a constant value means only one row can exist.
    # (true) is the same for every row, so the second row will violate uniqueness.
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_profile_singleton ON profile ((true))")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_profile_singleton")
