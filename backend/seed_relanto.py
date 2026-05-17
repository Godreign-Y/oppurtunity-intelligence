"""Seed Relanto service-company intelligence data."""

from app.db.session import SessionLocal
from app.services.service_intelligence.relanto_seed import seed_relanto


def main() -> None:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured.")
    db = SessionLocal()
    try:
        company = seed_relanto(db)
        print(f"Seeded service intelligence for {company.company_name}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
