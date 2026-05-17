"""
app/db/base.py

Declarative base for all SQLAlchemy ORM models.
Import all models here so Alembic can detect them during autogenerate.
"""

from app.db.base_class import Base  # noqa: F401
from app.models.signal import Signal  # noqa: F401
from app.models.company import Company  # noqa: F401
from app.models.market_pain import MarketPainSignal  # noqa: F401
from app.models.github_signal import GitHubSignal  # noqa: F401
from app.models.huggingface_signal import HuggingFaceSignal  # noqa: F401
from app.models.normalized_signal import NormalizedSignal  # noqa: F401
from app.models.raw_signal import RawSignal  # noqa: F401
from app.models.tracked_query import TrackedQuery  # noqa: F401
from app.models.funding_event import FundingEvent  # noqa: F401
from app.models.hiring_signal import HiringSignal  # noqa: F401
