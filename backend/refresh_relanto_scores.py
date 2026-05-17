"""Refresh persisted Relanto opportunity scores for fast UI retrieval."""

from app.db.session import SessionLocal
from app.services.service_intelligence.service import refresh_relanto_opportunity_scores


def main() -> None:
    db = SessionLocal()
    try:
        count = refresh_relanto_opportunity_scores(db)
        print(f"Refreshed {count} Relanto opportunity score rows.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
