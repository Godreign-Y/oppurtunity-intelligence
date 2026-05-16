"""
Base class for SQLAlchemy models.

This must be isolated to avoid importing async engine during migrations.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all models.
    """
    pass