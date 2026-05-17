# FastAPI backend plan

## Project bootstrap (uv + Python 3.11)

```bash
cd backend
uv init --package redit
# pyproject.toml: requires-python = ">=3.11,<3.12"
uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg psycopg[binary] alembic pydantic-settings praw vaderSentiment spacy transformers torch --optional  # trim torch if CPU-only path chosen
uv add --dev pytest httpx ruff mypy
```

Entry: `uv run uvicorn redit.main:app --reload --host 0.0.0.0 --port 8000`

## Application structure

```text
src/redit/
├── main.py                 # FastAPI app, lifespan (DB, models)
├── config.py               # Settings from env
├── api/
│   ├── router.py           # include all routers
│   ├── health.py
│   ├── ingestion.py
│   ├── intelligence.py
│   ├── config.py           # pipeline_config, subreddits
│   └── products.py         # known_products CRUD
├── services/
│   ├── ingestion_service.py
│   └── intelligence_service.py
├── pipeline/
│   └── orchestrator.py
├── ingestion/
├── filtering/
├── enrichment/
├── pain/
├── intelligence/
└── db/
    ├── session.py
    └── models/
```

## API surface (v1)

Base path: `/api/v1`

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | `{ "status": "ok" }` |
| GET | `/health/db` | Neon ping |

### Ingestion

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ingestion/runs` | Start pipeline run (background task) |
| GET | `/ingestion/runs` | List runs (paginated) |
| GET | `/ingestion/runs/{run_id}` | Run detail + counts (saved/rejected) |

**POST body:**

```json
{
  "subreddits": ["OpenAI"],
  "limit_per_subreddit": 100,
  "sort": "hot"
}
```

**Response `202`:**

```json
{
  "run_id": "uuid",
  "status": "queued"
}
```

Implementation: FastAPI `BackgroundTasks` for MVP; upgrade to job queue when runs exceed HTTP timeout.

### Intelligence (read/export)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/intelligence` | Filtered list |
| GET | `/intelligence/{id}` | Single record (full payload) |
| GET | `/intelligence/export` | JSON array download (`?format=json`) |

**Query params:** `subreddit`, `product`, `company`, `min_sentiment`, `workflow_pain_only`, `from`, `to`, `limit`, `offset`.

### Configuration

| Method | Path | Description |
|--------|------|-------------|
| GET | `/config/pipeline` | All threshold/keyword config |
| PATCH | `/config/pipeline` | Partial update (validated) |
| GET | `/config/subreddits` | Active targets |
| PUT | `/config/subreddits` | Replace or patch list |

### Known products

| Method | Path | Description |
|--------|------|-------------|
| GET | `/products` | Dictionary for enrichment |
| POST | `/products` | Add mapping |
| DELETE | `/products/{name}` | Remove |

## Pydantic schemas

- Request/response models in `redit.api.schemas`—separate from SQLAlchemy models.
- `IntelligenceRecordOut` exposes flat fields + optional `include_payload=true`.

## Lifespan events

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    load_nlp_models()  # classifier, optional spaCy
    yield
    await close_db_pool()
    unload_nlp_models()
```

## Error handling

| Code | When |
|------|------|
| 400 | Invalid config patch |
| 404 | Unknown run/record |
| 409 | Duplicate run still `running` (optional guard) |
| 503 | DB unreachable |

## Testing strategy

- `httpx.AsyncClient` against app with **test Neon branch** or Docker Postgres (same Alembic migrations).
- Integration test: inject fixture `RawPost` through orchestrator without PRAW.
- Reddit: manual/staging credentials only—no mock unless approved per `rules.md`.

## Dependencies alignment with PDF

| PDF requirement | Library |
|-----------------|---------|
| Reddit API | `praw` |
| Zero-shot / small classifier | `transformers` + `torch` (or `onnxruntime` later for size) |
| NER | `spacy` + `en_core_web_sm` |
| Sentiment MVP | `vaderSentiment` |

Keep versions pinned in `uv.lock`.

## OpenAPI

FastAPI auto-docs at `/docs` for frontend team; export OpenAPI JSON for optional client codegen in React (`openapi-typescript`).
