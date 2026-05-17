# REDIT — Product Pain Intelligence Pipeline

## Source of truth

Implementation follows **REDIT.pdf** (10-page production pipeline: Reddit → validated intelligence JSON). This project extracts **meaningful, market-relevant frustration signals** from targeted subreddits—not generic scraping or vague sentiment dashboards.

## Product question (Phase 0)

> What repeated technology/product frustrations are users discussing that indicate a potential business opportunity?

**In scope:** targeted ingestion, stream filtering, tech relevance, product/company linkage, business validation, frustration + workflow-pain detection, persisted intelligence records.

**Out of scope (for now):** whole-site Reddit dumps, generic “AI summaries,” Crunchbase/Clearbit enrichment (documented as Phase 3+ later).

## Mandated stack

| Layer | Choice | Notes |
|-------|--------|--------|
| Backend | **FastAPI** | Async HTTP, OpenAPI, background tasks / job queue later |
| Frontend | **Vite + React** | TypeScript recommended; talks to FastAPI only |
| Python | **3.11.x** | Pin in `pyproject.toml` (`requires-python = ">=3.11,<3.12"`) |
| Packages | **uv only** | `uv sync`, `uv run`; no pip/conda in docs or CI |
| Database | **Neon** (PostgreSQL) | Connection via `DATABASE_URL`; SSL required |
| Migrations | **Alembic** (required) | All schema changes through revisions; no ad-hoc DDL |
| Reddit | **PRAW** + Reddit API credentials | OAuth app: client id, secret, user agent |

## Engineering rules (from `rules.md`)

- Modular packages per pipeline phase; thin routers, fat domain services.
- Type hints on all functions/methods.
- Docstrings on every module, class, and function.
- No mocked “fake” Reddit or NLP in production paths without explicit approval.

## Document map

| Doc | Purpose |
|-----|---------|
| [01-ARCHITECTURE.md](./01-ARCHITECTURE.md) | Components, data flow, deployment |
| [02-PIPELINE-MAPPING.md](./02-PIPELINE-MAPPING.md) | PDF steps → code modules |
| [03-DATABASE-AND-ALEMBIC.md](./03-DATABASE-AND-ALEMBIC.md) | Neon schema, migrations, JSON storage |
| [04-BACKEND-API.md](./04-BACKEND-API.md) | FastAPI routes, jobs, config |
| [05-FRONTEND.md](./05-FRONTEND.md) | React screens and API usage |
| [06-MVP-ROADMAP.md](./06-MVP-ROADMAP.md) | Phased delivery and acceptance criteria |

## Repository layout (target)

```text
REDIT/
├── backend/
│   ├── pyproject.toml          # uv, Python 3.11
│   ├── uv.lock
│   ├── alembic.ini
│   ├── alembic/versions/
│   └── src/redit/
│       ├── main.py
│       ├── config.py
│       ├── api/                # routers
│       ├── db/                 # session, models
│       ├── ingestion/          # Phase 1: PRAW
│       ├── filtering/          # Phase 2: steps 3–5
│       ├── enrichment/         # Phase 3: steps 6–7
│       ├── pain/               # Phase 4: steps 8–9
│       └── intelligence/       # Phase 5: step 10
├── frontend/                   # Vite + React
├── docs/
├── .env.example
└── rules.md
```

## Environment variables (minimum)

```bash
# Neon
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require

# Reddit (PRAW)
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=redit-pain-intel/0.1 by <reddit_username>

# App
API_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:5173
```

## Success criteria (MVP)

1. Operator can trigger ingestion for configured subreddits (limited `hot` posts).
2. Stream pipeline applies PDF filters before any DB write.
3. Passing posts persist as **intelligence records** (JSON + indexed columns).
4. UI lists/filter exports validated intelligence.
5. All tables created/upgraded **only** via Alembic against Neon.
