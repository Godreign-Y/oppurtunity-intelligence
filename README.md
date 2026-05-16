# AI Opportunity Intelligence Platform

Transforms public technical behavior — career pages and engineering blogs — into structured commercial opportunity intelligence for IT service companies.

---

## Architecture

```
opportunity-intel/
├── backend/          # FastAPI + SQLAlchemy + Alembic
└── frontend/         # Vite + React + TypeScript
```

### Pipeline Overview

```
Company Name Input
        ↓
┌──────────────────────────────────────┐
│         Career Page Pipeline         │
│  ATS Discovery → Job Extraction →    │
│  Signal Normalization                │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│       Engineering Blog Pipeline      │
│  Blog Discovery → Article Fetch →   │
│  Signal Normalization                │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│           AI Inference Layer         │
│  Pain Correlation → Opportunity      │
│  Mapping → Explainability            │
└──────────────────────────────────────┘
        ↓
   Neon PostgreSQL Storage
```

---

## Quick Start

### Prerequisites

- Python 3.11
- Node.js 18+
- [UV](https://docs.astral.sh/uv/getting-started/installation/)
- A [Neon](https://neon.tech) account (free tier works)
- API keys for: Tavily, Serper, Firecrawl, OpenRouter

---

### Step 1 — Backend Setup

```bash
cd backend

# Install Python dependencies with UV
uv sync

# Configure environment
cp .env.example .env
# → Open .env and fill in DATABASE_URL, API keys

# Run database migrations (creates tables in Neon)
uv run alembic upgrade head

# Start FastAPI server
uv run uvicorn app.main:app --reload --port 8000
```

Backend runs at: **http://localhost:8000**  
API docs (Swagger): **http://localhost:8000/docs**

---

### Step 2 — Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## Environment Variables

All backend config is in `backend/.env`. Copy from `backend/.env.example`:

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | Neon PostgreSQL connection string |
| `TAVILY_API_KEY` | ✅ | [tavily.com](https://tavily.com) — web search for ATS + blog discovery |
| `SERPER_API_KEY` | ✅ | [serper.dev](https://serper.dev) — Google Search fallback |
| `FIRECRAWL_API_KEY` | ✅ | [firecrawl.dev](https://firecrawl.dev) — clean content extraction |
| `OPENROUTER_API_KEY` | ✅ | [openrouter.ai](https://openrouter.ai) — LLM inference |
| `LLM_MODEL` | ⚙️ | Default: `openai/gpt-4o-mini` |
| `CORS_ORIGINS` | ⚙️ | Default: `http://localhost:5173` |

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/analyze` | Run full analysis for a company |
| `GET` | `/api/v1/companies` | List tracked companies |
| `GET` | `/api/v1/companies/{name}/signals` | Get signals for a company |
| `GET` | `/health` | Health check |

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Vercel"}'
```

---

## Database Migrations (Alembic)

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Create a new migration after model changes
uv run alembic revision --autogenerate -m "add column xyz"

# Rollback one migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

---

## Supported ATS Platforms

| Platform | Priority | Method |
|---|---|---|
| Greenhouse | HIGH | Public JSON API |
| Lever | HIGH | Public JSON API |
| Ashby | MEDIUM | Firecrawl HTML extraction |
| Workday | LOW | Firecrawl HTML extraction |

---

## Pain Indicator Taxonomy

| Pain Type | Meaning |
|---|---|
| `scaling_pressure` | Infrastructure growth stress |
| `deployment_complexity` | DevOps inefficiency |
| `cloud_cost_pressure` | Infrastructure overspending |
| `reliability_issues` | Outages / stability problems |
| `legacy_modernization` | Old architecture modernization |
| `ai_adoption_uncertainty` | GenAI integration challenges |
| `security_pressure` | Security / compliance pressure |

---

## IDE Rules

See `backend/.cursor/rules.md` for all coding standards (UV, Alembic, type hints, docstrings, modularity).
