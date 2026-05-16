"""
add github_signal_id

Revision ID: 0ed33dc6393d
Revises: 2fbe0d04f2a9
Create Date: 2026-05-16
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = '0ed33dc6393d'
down_revision: Union[str, Sequence[str], None] = '2fbe0d04f2a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ✅ Add missing created_at column ONLY
    op.add_column(
        'normalized_signals',
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )


def downgrade():
    op.drop_column('normalized_signals', 'created_at')