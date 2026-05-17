"""
Normalization service using github_signals.
"""

import json
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.github_signal import GitHubSignal
from app.models.normalized_signal import NormalizedSignal

from app.normalization.rules import (
    detect_ecosystem,
    detect_severity,
    calculate_confidence,
)


# LOAD KEYWORDS FROM FILE
BASE_DIR = Path(__file__).resolve().parent.parent.parent
KEYWORDS_FILE = BASE_DIR / "normalization" / "keywords.json"

with open(KEYWORDS_FILE, "r") as f:
    SIGNAL_RULES = json.load(f)


def classify_signal(text: str):
    """
    Classify text using external keyword rules.
    """
    text = text.lower()

    for signal_type, keywords in SIGNAL_RULES.items():
        if any(keyword in text for keyword in keywords):
            return signal_type

    return "UNKNOWN"


class NormalizationService:

    def __init__(self, db: Session):
        self.db = db

    def run(self):

        result = self.db.execute(select(GitHubSignal))
        github_signals = result.scalars().all()

        for gh in github_signals:

            # Avoid duplicate normalization
            exists_query = select(NormalizedSignal).where(
                NormalizedSignal.github_signal_id == gh.id
            )
            existing = self.db.execute(exists_query).scalars().first()

            if existing:
                continue

            text = f"{gh.title} {gh.content}"

            normalized = NormalizedSignal(
                github_signal_id=gh.id,
                signal_type=classify_signal(text),
                severity=detect_severity(text),
                ecosystem=detect_ecosystem(text),
                confidence=calculate_confidence(text),
            )

            self.db.add(normalized)

        self.db.commit()