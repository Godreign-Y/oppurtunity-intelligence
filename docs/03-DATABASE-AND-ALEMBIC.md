# Database (Neon) and Alembic

## Connection

- **Driver:** SQLAlchemy 2.0 async with `asyncpg`.
- **URL format:** `postgresql+asyncpg://USER:PASSWORD@EP-xxx.neon.tech/neondb?sslmode=require`
- **Sync URL for Alembic:** `postgresql+psycopg://...` (Alembic migrations run sync; app runs async).

`alembic/env.py` will:

1. Load `DATABASE_URL` from environment.
2. Import all models from `redit.db.models` for autogenerate metadata.
3. Use `target_metadata = Base.metadata`.

**Rule:** No manual schema changes in Neon console for app tables—only `alembic revision` + `upgrade`.

## Entity relationship (MVP)

```mermaid
erDiagram
    ingestion_runs ||--o{ intelligence_records : produces
    ingestion_runs ||--o{ pipeline_rejects : logs
    subreddit_targets ||--o{ ingestion_runs : configures

    ingestion_runs {
        uuid id PK
        timestamptz started_at
        timestamptz finished_at
        string status
        jsonb config_snapshot
    }

    intelligence_records {
        uuid id PK
        string reddit_post_id UK
        uuid run_id FK
        string subreddit
        string product
        string company
        float tech_confidence
        float sentiment_score
        float business_relevance
        boolean workflow_pain_detected
        timestamptz reddit_created_at
        jsonb payload
        timestamptz created_at
    }

    pipeline_rejects {
        uuid id PK
        uuid run_id FK
        string reddit_post_id
        string stage
        string reason_code
        timestamptz created_at
    }

    subreddit_targets {
        string name PK
        boolean is_active
        int default_limit
    }

    pipeline_config {
        string key PK
        jsonb value
        timestamptz updated_at
    }

    known_products {
        string product_name PK
        string company_name
        boolean is_validated
    }
```

## Table definitions (logical)

### `subreddit_targets`

Seeded with PDF list. UI can toggle `is_active`.

### `pipeline_config`

Key-value JSON for thresholds and keyword lists. Allows runtime tuning without migration.

### `known_products`

Backed by PDF `KNOWN_PRODUCTS`; extend via admin API.

### `ingestion_runs`

Tracks each pipeline execution for UI status and auditing.

### `intelligence_records`

- **Indexed columns** for filtering (subreddit, product, company, scores, dates).
- **`payload` JSONB** holds full Step 10 document (source of truth for export).

### `pipeline_rejects` (recommended)

Lightweight reject log: `stage`, `reason_code`, `reddit_post_id`—no full body by default (GDPR/noise).

## Alembic workflow (uv only)

```bash
cd backend
uv sync
uv run alembic revision --autogenerate -m "initial schema"
uv run alembic upgrade head
```

### Revision strategy

| Revision | Contents |
|----------|----------|
| `001_initial` | All MVP tables + indexes |
| `002_seed_data` | Optional data migration: subreddits, known_products, default config |
| Future | Add columns via autogenerate; never edit applied revisions |

### Indexes

```sql
CREATE UNIQUE INDEX ix_intelligence_reddit_post_id ON intelligence_records (reddit_post_id);
CREATE INDEX ix_intelligence_subreddit_created ON intelligence_records (subreddit, reddit_created_at DESC);
CREATE INDEX ix_intelligence_product ON intelligence_records (product);
CREATE INDEX ix_intelligence_sentiment ON intelligence_records (sentiment_score);
CREATE INDEX ix_rejects_run_stage ON pipeline_rejects (run_id, stage);
```

JSONB: GIN index on `payload` only if query patterns need it (post-MVP).

## SQLAlchemy model sketch

```python
class IntelligenceRecord(Base):
    __tablename__ = "intelligence_records"

    id: Mapped[uuid.UUID]
    reddit_post_id: Mapped[str]  # unique
    run_id: Mapped[uuid.UUID]
    subreddit: Mapped[str]
    product: Mapped[str | None]
    company: Mapped[str | None]
    tech_confidence: Mapped[float]
    sentiment_score: Mapped[float]
    business_relevance: Mapped[float]
    workflow_pain_detected: Mapped[bool]
    reddit_created_at: Mapped[datetime]
    payload: Mapped[dict]  # JSONB
    created_at: Mapped[datetime]
```

All models in `redit.db.models` with matching Alembic versions.

## Neon operational notes

- Use **pooled** connection string for serverless FastAPI if connection count is a concern (`-pooler` host).
- Enable `statement_timeout` for long-running analytics queries (future).
- Branch per developer optional; production single branch for MVP.

## Data retention

- MVP: retain all intelligence records.
- Later: partition by month or archive cold JSON to object storage—still keyed in DB.
