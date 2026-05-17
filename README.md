# REDIT

AI-driven **Reddit market intelligence pipeline** — extract repeated technology/product frustrations that may signal business opportunities.

## Current (Phase 2+)

- **Global Reddit discovery** — `r/all`, `r/popular`, and `search.json` (no curated subreddit lists)
- **Semantic tech relevance** via `all-MiniLM-L6-v2` embeddings
- **Product/company extraction**, **VADER frustration**, **workflow/business validation**
- **Two API endpoints only** — ingestion + intelligence retrieval/export
- Validated intelligence JSON stored per run (in-memory; Neon later)

## Phase 1 (done)

- FastAPI backend with modular `src/redit` layout
- Reddit ingestion via **public JSON endpoints** (no OAuth required)
- Swappable `RedditSource` interface (PRAW stub for later)
- Streaming filtration pipeline (one post at a time; no blind bulk storage)

## Stack

| Component | Choice |
|-----------|--------|
| Python | 3.11.x |
| Packages | [uv](https://docs.astral.sh/uv/) only |
| API | FastAPI + Uvicorn |
| DB (next phase) | Neon + Alembic |

## Project layout

```text
REDIT/
├── pyproject.toml          # uv project root
├── .venv/                  # single shared environment
├── backend/
│   ├── src/redit/
│       ├── api/           # HTTP routes
│       ├── config/        # Settings
│       ├── filters/       # Stream filter stages
│       ├── ingestion/     # RedditSource + public JSON
│       ├── models/        # Pydantic schemas
│       ├── pipelines/     # Orchestrator
│       ├── services/      # IngestionService
│       ├── storage/       # Run store (in-memory Phase 1)
│       └── utils/         # Logging
├── docs/                  # Architecture & roadmap
├── .env.example
└── rules.md
```

## Quick start

### 1. Prerequisites

- Python **3.11**
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### 2. Environment

```bash
cp .env.example .env
```

Edit `.env` — set a descriptive `REDDIT_USER_AGENT` (Reddit requires this).

### 3. Install & run

From the **project root** (`REDIT/`):

```bash
uv sync
uv run uvicorn redit.main:app --reload --host 0.0.0.0 --port 8000
```

On OneDrive paths, if `uv sync` fails on hardlinks, use: `set UV_LINK_MODE=copy` (Windows) before sync.

API docs: http://localhost:8000/docs

### 4. API (2 endpoints)

**Ingest** global Reddit → pipeline → store intelligence:

```bash
curl -X POST http://localhost:8000/api/v1/ingestion \
  -H "Content-Type: application/json" \
  -d "{\"feeds\":[\"all\",\"popular\"],\"limit_per_source\":25}"
```

**Retrieve intelligence** (use `run_id` from ingestion response):

```bash
curl http://localhost:8000/api/v1/intelligence/{run_id}
curl "http://localhost:8000/api/v1/intelligence/{run_id}?export=true" -o intelligence.json
```

First startup downloads the sentence-transformer model (~90MB).

## Switching to PRAW later

1. Set `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` in `.env`
2. Implement `PrawRedditSource` in `ingestion/praw_source.py`
3. Set `REDDIT_SOURCE=praw`

No changes required in `pipelines/`, `filters/`, or `services/`.

## Tests

```bash
uv sync --extra dev
uv run pytest
```

## Documentation

See [`docs/`](docs/) for full architecture, pipeline mapping, and MVP roadmap.
