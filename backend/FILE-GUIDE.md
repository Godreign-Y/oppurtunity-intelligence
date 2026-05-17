# Backend file guide

Short reference for every file under `backend/`. The **uv project root** is the parent `REDIT/` folder (`pyproject.toml`, `.venv`); this folder holds the Python package and tests.

```text
REDIT/                    ← run `uv sync` and `uv run` here
├── pyproject.toml
├── .venv/
└── backend/
    ├── FILE-GUIDE.md     ← this document
    └── src/redit/        ← import name: `redit`
```

---

## Package entry

| File | Purpose |
|------|---------|
| `src/redit/__init__.py` | Package marker; exposes `__version__`. |
| `src/redit/main.py` | FastAPI app factory, lifespan (load ML models, in-memory store), CORS, and `uvicorn` CLI entry (`redit-api`). |

---

## `api/` — HTTP layer (2 public endpoints)

| File | Purpose |
|------|---------|
| `api/__init__.py` | Package marker for API routers. |
| `api/router.py` | Registers ingestion + intelligence routers on the app. |
| `api/deps.py` | FastAPI dependencies: settings, run store, model registry, services. |
| `api/ingestion.py` | **POST `/api/v1/ingestion`** — starts global Reddit discovery + pipeline run. |
| `api/intelligence.py` | **GET `/api/v1/intelligence/{run_id}`** — returns intelligence JSON; `?export=true` for file download. |

---

## `config/` — environment and defaults

| File | Purpose |
|------|---------|
| `config/__init__.py` | Re-exports `Settings` and `get_settings()`. |
| `config/settings.py` | Pydantic settings from `.env`: Reddit, discovery feeds/search, filter thresholds, ML model names. |

---

## `ingestion/` — fetch Reddit (swappable source)

| File | Purpose |
|------|---------|
| `ingestion/__init__.py` | Exports `RedditSource` and `create_reddit_source()`. |
| `ingestion/base.py` | Abstract interface: `iter_global_feed()` (r/all, r/popular) and `iter_search()`. |
| `ingestion/public_json.py` | **Current implementation** — Reddit public `.json` endpoints via `httpx`. |
| `ingestion/praw_source.py` | **Future** — PRAW stub when official API credentials exist. |
| `ingestion/factory.py` | Builds `public_json` or `praw` source from `REDDIT_SOURCE` env. |
| `ingestion/discovery_stream.py` | Merges feeds + search into one stream; **dedupes** posts by Reddit id. |

---

## `filters/` — one-post-at-a-time pipeline stages

| File | Purpose |
|------|---------|
| `filters/__init__.py` | Exports `FilterStage` and `build_filter_pipeline()`. |
| `filters/base.py` | Abstract filter contract: `apply(post, context) → FilterResult`. |
| `filters/registry.py` | Builds ordered stage list: metadata → semantic → product → sentiment → workflow → business. |
| `filters/metadata.py` | Cheap gates: min text length, min upvotes, recency window. |
| `filters/semantic.py` | **ML** — MiniLM embedding similarity; rejects non–tech/product posts. |
| `filters/product.py` | Dictionary product/company extraction + business validation gate. |
| `filters/sentiment.py` | **VADER** — rejects posts without frustration/negative tone. |
| `filters/workflow.py` | Keyword detection for workflow/enterprise pain; boosts business relevance score. |
| `filters/tech_keywords.py` | Optional legacy keyword pre-filter (off by default; not in active pipeline). |
| `filters/embeddings.py` | Placeholder for future per-post embeddings (not in active pipeline). |
| `filters/clustering.py` | Placeholder for future batch clustering (not in active pipeline). |

---

## `pipelines/` — orchestration

| File | Purpose |
|------|---------|
| `pipelines/__init__.py` | Exports `PipelineContext` (avoids circular imports with filters). |
| `pipelines/context.py` | Per-post accumulator: merges metadata from each passed stage. |
| `pipelines/orchestrator.py` | Runs stages in order; stops on first reject; builds `IntelligenceRecord` on full pass. |

---

## `models/` — Pydantic schemas

| File | Purpose |
|------|---------|
| `models/__init__.py` | Public re-exports of domain/API models. |
| `models/reddit.py` | `RawRedditPost` — normalized post from any Reddit source. |
| `models/discovery.py` | `GlobalFeed` type (`all` \| `popular`). |
| `models/pipeline.py` | Run request/response, filter results, reject records, run summary. |
| `models/intelligence.py` | **Step-10 output** — validated intelligence JSON schema (`IntelligenceRecord`). |

---

## `services/` — application logic

| File | Purpose |
|------|---------|
| `services/__init__.py` | Exports `IngestionService` and `IntelligenceService`. |
| `services/ingestion_service.py` | Discovery fetch → pipeline per post → store only passed intelligence. |
| `services/intelligence_service.py` | Read/export intelligence records for a `run_id`. |

---

## `storage/` — persistence (in-memory for now)

| File | Purpose |
|------|---------|
| `storage/__init__.py` | Exports `RunStore` and `InMemoryRunStore`. |
| `storage/base.py` | Abstract store: runs + intelligence records (Neon later). |
| `storage/memory.py` | In-memory implementation used at startup. |

---

## `intelligence/` — validated output builder

| File | Purpose |
|------|---------|
| `intelligence/__init__.py` | Exports `IntelligenceBuilder`. |
| `intelligence/builder.py` | Maps `RawRedditPost` + pipeline context → `IntelligenceRecord` JSON. |

---

## `ml/` — local CPU models (loaded once at startup)

| File | Purpose |
|------|---------|
| `ml/__init__.py` | Exports `ModelRegistry`. |
| `ml/registry.py` | Loads sentence-transformer + VADER at app lifespan; shared by filters. |
| `ml/tech_relevance.py` | Cosine similarity vs tech/non-tech anchor phrases. |
| `ml/sentiment.py` | VADER wrapper; frustration threshold logic. |

---

## `data/` — static reference data

| File | Purpose |
|------|---------|
| `data/__init__.py` | Package marker. |
| `data/known_products.py` | Product → company map and `extract_product_company()` helper. |

---

## `utils/` — shared helpers

| File | Purpose |
|------|---------|
| `utils/__init__.py` | Exports logging helpers. |
| `utils/logging.py` | Configures structured console logging for the app. |

---

## Generated / tooling (safe to ignore in git)

| Path | Purpose |
|------|---------|
| `src/redit.egg-info/` | Created by `uv sync` / setuptools; package metadata (do not edit). |

---

## Data flow (how files connect)

```text
POST /ingestion
    → ingestion_service
        → discovery_stream → public_json (r/all, r/popular, search)
        → orchestrator
            → filters (metadata → semantic → … → business)
            → intelligence/builder
        → storage/memory (IntelligenceRecord only)

GET /intelligence/{run_id}
    → intelligence_service → storage/memory
```

---

## Tests

| Path | Purpose |
|------|---------|
| `tests/` | Pytest unit tests (run from repo root: `uv run pytest backend/tests`). |

If `tests/` is missing locally, add tests under `backend/tests/` — paths are configured in root `pyproject.toml`.
