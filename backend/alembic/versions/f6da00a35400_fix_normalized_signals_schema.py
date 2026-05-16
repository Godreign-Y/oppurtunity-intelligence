"""
fix normalized_signals schema
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# ✅ REQUIRED: Alembic identifiers (THIS IS WHAT WAS MISSING)
revision: str = 'f6da00a35400'
down_revision: Union[str, Sequence[str], None] = '0ed33dc6393d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    columns = [c["name"] for c in inspector.get_columns("normalized_signals")]

    # ✅ Add created_at only if missing
    if "created_at" not in columns:
        op.add_column(
            "normalized_signals",
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )

    # ✅ Fix raw_signal_id NOT NULL constraint
    try:
        op.alter_column(
            "normalized_signals",
            "raw_signal_id",
            existing_type=sa.Integer(),
            nullable=True
        )
    except Exception:
        pass


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("normalized_signals")]

    if "created_at" in columns:
        op.drop_column("normalized_signals", "created_at")
