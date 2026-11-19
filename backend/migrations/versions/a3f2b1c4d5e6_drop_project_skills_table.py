"""drop_project_skills_table

Revision ID: a3f2b1c4d5e6
Revises: caab5a516f3a
Create Date: 2026-11-19 00:00:00.000000

ProjectSkill was a planned many-to-many join between projects and skills.
It was never used in the application layer (no router, no UI, no queries).
Dropping the table to reduce schema complexity.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a3f2b1c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'caab5a516f3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('project_skills')


def downgrade() -> None:
    op.create_table(
        'project_skills',
        sa.Column('project_id', postgresql.UUID(), nullable=False),
        sa.Column('skill_id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id', 'skill_id'),
    )
