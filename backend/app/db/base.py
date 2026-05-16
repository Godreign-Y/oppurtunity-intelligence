"""
app/db/base.py

Declarative base for all SQLAlchemy ORM models.
Import all models here so Alembic can detect them during autogenerate.
"""

from app.db.base_class import Base  # noqa: F401
from app.models.signal import Signal  # noqa: F401
from app.models.company import Company  # noqa: F401
