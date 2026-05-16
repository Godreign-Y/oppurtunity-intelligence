# Opportunity Intelligence Platform — Backend

FastAPI backend for extracting intelligence signals from career pages and engineering blogs.

## Tech Stack

- **Python 3.11**
- **FastAPI** — REST API
- **SQLAlchemy 2.0** — ORM
- **Alembic** — database migrations
- **Neon** — PostgreSQL (cloud-hosted)
- **UV** — Python package manager
- **OpenRouter** — LLM inference (GPT-4o-mini via OpenAI-compatible API)
- **Tavily + Serper** — web search APIs
- **Firecrawl** — clean markdown extraction from web pages
- **feedparser** — RSS feed parsing

---

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── analyze.py       # POST /api/v1/analyze
│   │       │   └── signals.py       # GET /api/v1/companies, /signals
│   │       └── router.py
│   ├── core/
│   │   └── config.py                # Settings from env vars
│   ├── db/
│   │   ├── base.py                  # Declarative base + model imports
│   │   └── session.py               # DB engine + session factory
│   ├── models/
│   │   ├── company.py               # Company ORM model
│   │   └── signal.py                # Signal ORM model
│   ├── schemas/
│   │   ├── company.py               # Pydantic company schemas
│   │   └── signal.py                # Pydantic signal schemas
│   ├── services/
│   │   ├── career/
│   │   │   ├── ats_discovery.py     # ATS platform detection via search
│   │   │   ├── ats_extractor.py     # Greenhouse, Lever, Ashby, Workday extractors
│   │   │   ├── signal_extractor.py  # Job → UnifiedSignalSchema conversion
│   │   │   └── pipeline.py          # Career pipeline orchestrator
│   │   ├── blog/
│   │   │   ├── blog_discovery.py    # Engineering blog URL discovery
│   │   │   ├── blog_extractor.py    # RSS + Firecrawl article extraction
│   │   │   ├── signal_extractor.py  # Article → UnifiedSignalSchema conversion
│   │   │   └── pipeline.py          # Blog pipeline orchestrator
│   │   ├── ai/
│   │   │   └── inference.py         # LLM-based opportunity inference
│   │   └── company_service.py       # CRUD for Company + Signal records
│   ├── utils/
│   │   ├── search.py                # Tavily + Serper search helpers
│   │   ├── firecrawl.py             # Firecrawl extraction helper
│   │   └── normalization.py         # Unified Signal Schema normalization
│   └── main.py                      # FastAPI app entry point
├── alembic/
│   ├── versions/
│   │   └── 0001_initial.py          # Initial DB migration
│   ├── env.py
│   └── script.py.mako
├── .cursor/
│   └── rules.md                     # IDE rules
├── alembic.ini
├── pyproject.toml
└── .env.example
```

---

## Setup

### 1. Prerequisites

- Python 3.11 installed
- [UV](https://docs.astral.sh/uv/getting-started/installation/) installed
- A [Neon](https://neon.tech) PostgreSQL database created
- API keys: Tavily, Serper, Firecrawl, OpenRouter

### 2. Install dependencies

```bash
cd backend
uv sync
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in all required values
```

Required variables:
| Variable | Description |
|---|---|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `TAVILY_API_KEY` | Tavily Search API key |
| `SERPER_API_KEY` | Serper (Google Search) API key |
| `FIRECRAWL_API_KEY` | Firecrawl API key |
| `OPENROUTER_API_KEY` | OpenRouter LLM API key |

### 4. Run database migrations

```bash
uv run alembic upgrade head
```

### 5. Start the server

```bash
uv run uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/analyze` | Trigger full company analysis pipeline |
| `GET` | `/api/v1/companies` | List all tracked companies |
| `GET` | `/api/v1/companies/{name}/signals` | Get signals for a company |
| `GET` | `/health` | Health check |

### Example: Analyze a company

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Vercel"}'
```

---

## Adding a new Alembic migration

```bash
uv run alembic revision --autogenerate -m "describe your change"
uv run alembic upgrade head
```

## IDE Rules

See `.cursor/rules.md` for project coding standards.
