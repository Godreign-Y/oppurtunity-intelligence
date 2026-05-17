# MVP roadmap and delivery phases

## Milestone 0 — Repository skeleton (Day 1)

- [ ] `backend/` with `uv`, Python 3.11 pin, `src/redit` package
- [ ] `frontend/` Vite React TS
- [ ] `.env.example` for Neon + Reddit
- [ ] Alembic initialized; `001_initial` migration applied to Neon dev branch
- [ ] FastAPI health + DB health endpoints

**Exit:** `uv run alembic upgrade head` succeeds; UI loads empty dashboard.

---

## Milestone 1 — Ingestion only (Phase 1 PDF)

- [ ] PRAW client + config validation
- [ ] `subreddit_targets` seed migration
- [ ] `POST /ingestion/runs` fetches posts **without** persisting posts table
- [ ] Run logging in `ingestion_runs`

**Exit:** Run completes; logs show N posts fetched per subreddit (dry-run mode flag).

---

## Milestone 2 — Stream filters (Phase 2 PDF, Steps 3–5)

- [ ] Metadata filter module + reject logging
- [ ] Tech keyword filter
- [ ] Classifier loaded at startup; Step 5 integrated
- [ ] `pipeline_config` API for thresholds

**Exit:** Same run reports rejected counts by `reason_code`; zero DB intelligence rows yet.

---

## Milestone 3 — Enrichment + pain (Phases 3–4 PDF, Steps 6–9)

- [ ] `known_products` table + API
- [ ] Product dictionary matcher
- [ ] Business validation rules
- [ ] VADER sentiment + workflow keyword detector
- [ ] Policy: when to pass without product name

**Exit:** Dry-run logs show sample intelligence JSON in stdout for manual review.

---

## Milestone 4 — Persist intelligence (Phase 5 PDF, Step 10)

- [ ] `intelligence_records` write path
- [ ] Idempotent `reddit_post_id`
- [ ] `GET /intelligence` + export endpoint
- [ ] Full orchestrator wired to ingestion run

**Exit:** End-to-end run stores only posts passing all stages; API returns records.

---

## Milestone 5 — Frontend operator UI

- [ ] Dashboard + run trigger
- [ ] Intelligence explorer with filters + export
- [ ] Settings for subreddits, pipeline config, products

**Exit:** Non-developer can configure, run, and download JSON from UI.

---

## Milestone 6 — Hardening

- [ ] Structured logging + run metrics
- [ ] Rate limit / error handling for PRAW
- [ ] Basic pytest coverage for filters (fixture posts from PDF examples)
- [ ] README: setup with uv, Neon, Alembic, Reddit app

**Exit:** Repeatable local setup documented; CI runs ruff + pytest (no secrets).

---

## Post-MVP (documented, not scheduled)

| Item | PDF reference |
|------|----------------|
| Crunchbase / Clearbit business validation | Step 7 later |
| Transformer sentiment | Step 8 better |
| LLM extraction for products/pain | Steps 6, 9 |
| Clustering → market-gap JSON | Title / beyond page 10 |
| Job queue for long runs | Architecture note |
| Comment thread ingestion | Phase 1 extension |

---

## Acceptance test script (manual)

1. Set Reddit credentials and Neon `DATABASE_URL`.
2. `uv run alembic upgrade head`.
3. Start API and frontend.
4. Confirm default subreddits in settings.
5. Trigger run with `limit_per_subreddit: 10` on one subreddit.
6. Verify run completes; `intelligence` list non-empty (or rejects explain empty).
7. Open record detail—payload matches schema in `02-PIPELINE-MAPPING.md`.
8. Export JSON file; validate required fields present.

---

## Risk register

| Risk | Mitigation |
|------|------------|
| Reddit API rate limits | Low limits in MVP; exponential backoff |
| NLP model size / CPU | Start VADER + keywords; lazy-load classifier; consider ONNX |
| Neon cold starts | Connection pool; small batch sizes |
| False negatives in filters | `pipeline_rejects` analytics; tunable config without code change |
| PRAW vs official API changes | Pin `praw` version; monitor deprecations |

---

## Definition of done (project MVP)

The system answers the Phase 0 question at **sample scale**: operators can repeatedly ingest targeted subreddits, filter to frustrated tech/product discussions, and query/export structured intelligence JSON from Neon via FastAPI and the React UI—with **every schema change managed by Alembic**.
