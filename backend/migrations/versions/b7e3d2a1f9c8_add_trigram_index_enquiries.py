"""add_trigram_index_enquiries

Revision ID: b7e3d2a1f9c8
Revises: a3f2b1c4d5e6
Create Date: 2026-11-19 00:01:00.000000

Adds pg_trgm GIN indexes on enquiries(name, email, subject) so that
ILIKE '%term%' searches use an index instead of full table scans.
"""
from typing import Sequence, Union
from alembic import op

revision: str = 'b7e3d2a1f9c8'
down_revision: Union[str, Sequence[str], None] = 'a3f2b1c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable the pg_trgm extension (safe to run multiple times)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    # GIN indexes for fast ILIKE '%term%' on the three searchable columns
    op.execute("CREATE INDEX IF NOT EXISTS ix_enquiries_name_trgm ON enquiries USING GIN (name gin_trgm_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_enquiries_email_trgm ON enquiries USING GIN (email gin_trgm_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_enquiries_subject_trgm ON enquiries USING GIN (subject gin_trgm_ops)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_enquiries_subject_trgm")
    op.execute("DROP INDEX IF EXISTS ix_enquiries_email_trgm")
    op.execute("DROP INDEX IF EXISTS ix_enquiries_name_trgm")
