# Opportunity Intelligence Platform — Comprehensive Analysis

---

## Part 1: Pipeline-by-Pipeline Quality Audit

### Inventory of Pipelines

| # | Pipeline | Orchestrator | Core Service | LLM-Powered? |
|---|----------|-------------|--------------|---------------|
| 1 | Blog | [blog_pipeline.py](file:///c:/code/hiring-pipeline/backend/app/pipelines/blog_pipeline.py) | [services/blog/pipeline.py](file:///c:/code/hiring-pipeline/backend/app/services/blog/pipeline.py) | ✅ |
| 2 | Career | [career_pipeline.py](file:///c:/code/hiring-pipeline/backend/app/pipelines/career_pipeline.py) | [services/career/pipeline.py](file:///c:/code/hiring-pipeline/backend/app/services/career/pipeline.py) | ✅ |
| 3 | Funding | [funding_pipeline.py](file:///c:/code/hiring-pipeline/backend/app/pipelines/funding_pipeline.py) | [services/funding/service.py](file:///c:/code/hiring-pipeline/backend/app/services/funding/service.py) | ✅ |
| 4 | GitHub Issues | [github_issues_pipeline.py](file:///c:/code/hiring-pipeline/backend/app/pipelines/github_issues_pipeline.py) | [services/github/service.py](file:///c:/code/hiring-pipeline/backend/app/services/github/service.py) | ✅ |
| 5 | Hiring Signals | [hiring_signals_pipeline.py](file:///c:/code/hiring-pipeline/backend/app/pipelines/hiring_signals_pipeline.py) | [services/hiring/service.py](file:///c:/code/hiring-pipeline/backend/app/services/hiring/service.py) | ✅ |
| 6 | Reddit / Market Pain | [reddit_pipeline.py](file:///c:/code/hiring-pipeline/backend/app/pipelines/reddit_pipeline.py) | [services/market_pain/pipeline.py](file:///c:/code/hiring-pipeline/backend/app/services/market_pain/pipeline.py) | ✅ |

**Cross-cutting layers:**
- Orchestrator: [pipeline_worker.py](file:///c:/code/hiring-pipeline/backend/app/services/pipeline_worker.py)
- Normalization: [normalization/service.py](file:///c:/code/hiring-pipeline/backend/app/services/normalization/service.py)
- Insights: [insights/service.py](file:///c:/code/hiring-pipeline/backend/app/services/insights/service.py)
- Service Intelligence: [service_intelligence/service.py](file:///c:/code/hiring-pipeline/backend/app/services/service_intelligence/service.py)
- Outreach: [outreach/service.py](file:///c:/code/hiring-pipeline/backend/app/services/outreach/service.py)

---

### 1. Blog Pipeline

**Flow:** Discover blog URL → Extract posts → LLM signal extraction

**Effectiveness: 🟡 Medium**

| Aspect | Rating | Details |
|--------|--------|---------|
| Discovery | 🟡 | Tries 10 hardcoded URL patterns, then falls back to Google search. Misses subdomains (e.g., `blog.company.com`, `medium.com/company`) and custom paths. |
| Extraction | 🔴 | Sequentially crawls each post URL — no concurrency, no rate limiting, no retry. For 20 posts this could take minutes and hit Firecrawl rate limits. |
| LLM Analysis | 🟡 | Decent prompt with 7 signal categories, but content truncated at 8000 chars — long posts lose critical information. |
| Error Handling | 🟡 | Top-level try/catch returns empty signals, but individual post failures are silently swallowed with `continue`. |
| Data Persistence | 🔴 | **Signals are NOT saved to the database.** They are returned in-memory only. |

**Unprofessional Code Issues:**
- [blog_extractor.py](file:///c:/code/hiring-pipeline/backend/app/services/blog/blog_extractor.py) — `_filter_blog_links` uses a naive heuristic (path depth) that would match `/about`, `/contact`, `/privacy` etc. as "blog posts"
- [signal_extractor.py](file:///c:/code/hiring-pipeline/backend/app/services/blog/signal_extractor.py) — `prompt_template` parameter is filled with the full prompt but `text=""` is passed as empty — the `{text}` placeholder pattern in `AIInferenceService` is bypassed, creating a confusing contract

---

### 2. Career Pipeline

**Flow:** Discover career/ATS page → Extract listings → LLM signal extraction → Aggregate analysis

**Effectiveness: 🟡 Medium**

| Aspect | Rating | Details |
|--------|--------|---------|
| Discovery | 🟢 | Good coverage — checks 8 URL patterns + 8 ATS platforms (Greenhouse, Lever, Workday, etc.) |
| Extraction | 🟡 | Sequential crawling, regex-based link filtering. `_parse_listings_from_content` fallback is very naive — matches any line containing "engineer", "developer", etc. |
| LLM Analysis | 🟢 | Well-structured two-phase analysis: individual signal extraction + aggregate hiring velocity |
| Error Handling | 🟡 | Same pattern — individual failures silently swallowed |
| Data Persistence | 🔴 | **Not persisted to DB** — signals only exist in the response |

**Unprofessional Code Issues:**
- [ats_extractor.py](file:///c:/code/hiring-pipeline/backend/app/services/career/ats_extractor.py) — `_parse_listings_from_content` is extremely brittle. It splits content by newlines and checks for keywords, which would produce massive false positives on any page that mentions those words in non-job contexts
- The `text=""` pattern is repeated here (signals passed directly in the prompt template, `text` parameter unused)

---

### 3. Funding Pipeline

**Flow:** Google search → Classify snippets → Crawl articles → LLM detail extraction

**Effectiveness: 🟡 Medium**

| Aspect | Rating | Details |
|--------|--------|---------|
| Discovery | 🟡 | Only uses Google search (`"company funding round investment"`). Single query pattern limits recall. |
| RSS Integration | 🔴 | **RSS fetcher is a stub** — `_fetch_single_feed` returns empty list with a `# TODO: Implement proper RSS parsing` comment |
| Classification | 🟢 | Two-phase: quick snippet classification → full article extraction. Good confidence threshold (0.5) |
| LLM Analysis | 🟢 | Well-structured extraction prompt with 10 data fields |
| Error Handling | 🟢 | Best error handling of all pipelines — falls back to basic event from search result if full extraction fails |
| Data Persistence | 🔴 | **Not persisted.** `FundingEvent` model exists but is never used for writing |

**Unprofessional Code Issues:**
- [rss_fetcher.py](file:///c:/code/hiring-pipeline/backend/app/services/funding/rss_fetcher.py) — The entire RSS module is a dead-code stub. The TODO has not been implemented. This means one of the stated data sources (TechCrunch RSS, Crunchbase RSS) is **completely non-functional**
- [funding_pipeline.py](file:///c:/code/hiring-pipeline/backend/app/pipelines/funding_pipeline.py) — The pipeline orchestrator re-maps the service response into a new dict format, duplicating and potentially losing fields. This transformation layer adds no value

---

### 4. GitHub Issues Pipeline

**Flow:** Discover GitHub org → Fetch repos → Fetch issues → LLM analysis

**Effectiveness: 🟡 Medium**

| Aspect | Rating | Details |
|--------|--------|---------|
| Discovery | 🟡 | Google search for `"company github organization site:github.com"` — works for well-known companies, fails for companies using different org names |
| Data Fetching | 🟢 | Proper GitHub API usage with pagination, auth headers, and PR filtering |
| Analysis | 🟡 | Sends issue titles in bulk to LLM — loses body content, label context, and comment discussions |
| Rate Limiting | 🔴 | **No GitHub API rate limit handling.** For orgs with many repos, this will hit the 5000 req/hour limit |
| Data Persistence | 🔴 | **Not persisted.** `GitHubSignal` model exists but is never written to |

**Unprofessional Code Issues:**
- [client.py](file:///c:/code/hiring-pipeline/backend/app/services/github/client.py) — Hardcodes `max_repos=30` in the default but `get_repo_issues` doesn't handle pagination (only fetches first page)
- [service.py](file:///c:/code/hiring-pipeline/backend/app/services/github/service.py) — `fetch_issues` limits to top 10 repos but has no sorting criteria for which 10 to pick. The API call uses `sort=updated`, but the loop just takes the first 10 from the API response
- Issue body content is completely ignored in the LLM analysis — only titles and labels are sent. This loses the most valuable signal data

---

### 5. Hiring Signals Pipeline

**Flow:** Multi-source job search → Crawl listings → Process → LLM signal generation

**Effectiveness: 🟡 Medium**

| Aspect | Rating | Details |
|--------|--------|---------|
| Discovery | 🟡 | Searches 4 query patterns across Google. Good deduplication by URL. |
| Content Enrichment | 🟡 | Attempts to crawl each listing URL for full content — sequential, slow, no concurrency |
| Processing | 🔴 | `HiringProcessor` is essentially a no-op — it just renames fields. Adds no real value |
| LLM Analysis | 🟢 | Good prompt covering 6 signal dimensions |
| Keyword Filtering | 🟡 | Simple case-insensitive substring matching — no stemming, no fuzzy matching |
| Data Persistence | 🔴 | **Not persisted.** `HiringSignal` model exists but is unused |

**Unprofessional Code Issues:**
- [processor.py](file:///c:/code/hiring-pipeline/backend/app/services/hiring/processor.py) — This entire file is 23 lines. It's a field-renaming passthrough masquerading as a "processor." No actual processing (deduplication, normalization, enrichment) happens here
- [fetcher.py](file:///c:/code/hiring-pipeline/backend/app/services/hiring/fetcher.py) — Fetches from Google Search results, not from actual job board APIs (LinkedIn, Indeed have APIs). Google search results for jobs are unreliable and often return company info pages, not actual listings

---

### 6. Reddit / Market Pain Pipeline

**Flow:** Fetch subreddit posts → Metadata filter → Relevance classify → Frustration detect → Entity extract → Business validate → Workflow pain detect → Capability map → Score → Temporal analyze

**Effectiveness: 🟢 Good (best pipeline)**

| Aspect | Rating | Details |
|--------|--------|---------|
| Architecture | 🟢 | Most modular pipeline. 10+ analysis stages with clean separation |
| Metadata Filtering | 🟢 | Smart pre-filtering (upvotes, comments, content length, age) before expensive LLM calls |
| LLM Analysis | 🟡 | **5 separate LLM calls per post** (relevance, frustration, entity, business validation, workflow). Very expensive — 100 relevant posts = 500 API calls |
| Scoring | 🟢 | Well-designed composite scoring with configurable weights |
| Capability Mapping | 🟢 | Good keyword matching to Relanto's service portfolio |
| Data Persistence | 🔴 | **Not persisted.** `MarketPain` model exists with a very rich schema but is never written to |

**Unprofessional Code Issues:**
- [pipeline.py](file:///c:/code/hiring-pipeline/backend/app/services/market_pain/pipeline.py) — All 5 LLM calls are sequential per post with no batching, no concurrency (`asyncio.gather`), and no caching. Processing 50 posts would require **250 LLM API calls** running one at a time
- [reddit_client.py](file:///c:/code/hiring-pipeline/backend/app/services/market_pain/reddit_client.py) — The OAuth token is fetched once but never refreshed. Reddit tokens expire in 1 hour. After that, all requests silently fail
- [scoring.py](file:///c:/code/hiring-pipeline/backend/app/services/market_pain/scoring.py) — `recency_score` is hardcoded to `0.5` with a comment "placeholder — would need timestamp comparison." The data IS available in `posted_at` but isn't used
- [temporal_analysis.py](file:///c:/code/hiring-pipeline/backend/app/services/market_pain/temporal_analysis.py) — `_determine_trend` is just a volume bucket (>20 = "high_volume", etc.). No actual temporal trend analysis (week-over-week, acceleration, etc.)

---

### 7. Pipeline Worker (Orchestration Layer)

[pipeline_worker.py](file:///c:/code/hiring-pipeline/backend/app/services/pipeline_worker.py)

**Effectiveness: 🟡 Medium**

| Aspect | Rating | Details |
|--------|--------|---------|
| Concurrency | 🟢 | Uses `asyncio.gather` to run all 6 pipelines concurrently |
| Error Isolation | 🟢 | `return_exceptions=True` prevents one pipeline failure from crashing all |
| Run Tracking | 🟡 | Creates `PipelineRun` record but only tracks basic metadata (start, end, count) |
| Normalization | 🟡 | Normalizes signals but doesn't persist them |
| Insight Generation | 🟡 | Generates LLM insights but doesn't persist them |

**Unprofessional Code Issues:**
- Pipeline selection logic is a manual if/elif chain for 6 pipelines instead of a registry pattern. Adding a new pipeline requires modifying this file in multiple places
- `company_id` parameter is accepted but never used
- The worker creates `PipelineRun` and commits immediately, then later updates it. If the process crashes between these points, the run stays in "running" status forever — no cleanup/timeout mechanism

---

### 8. Cross-Cutting Concerns

#### AI Inference Service
[inference.py](file:///c:/code/hiring-pipeline/backend/app/services/ai/inference.py)

- 🔴 **No retry logic.** OpenAI API calls fail with rate limits, timeouts, etc. — there's zero retry/backoff
- 🔴 **No token counting.** Content is truncated by character count (8000 chars) not token count. This can still exceed context limits
- 🔴 **No cost tracking.** No logging of token usage, no budget controls
- 🟡 JSON parsing is fragile — looks for ` ```json ``` ` markers but doesn't handle cases where LLM responds without them consistently
- 🟡 The `text` parameter in `analyze_text` uses `prompt_template.format(text=text)`, but most callers pass `text=""` and embed everything in the template — inconsistent contract

#### HTTP Utility
[http.py](file:///c:/code/hiring-pipeline/backend/app/utils/http.py)

- 🔴 **No retry logic.** Single attempt, no exponential backoff
- 🔴 **No rate limiting.** Will hammer external APIs
- 🟡 Creates a new `httpx.AsyncClient` for every request — no connection pooling

#### Firecrawl Utility
[firecrawl.py](file:///c:/code/hiring-pipeline/backend/app/utils/firecrawl.py)

- 🔴 Uses Firecrawl v0 API (`/v0/scrape`) — this may be deprecated
- 🟡 No rate limiting for Firecrawl API calls

#### Database Layer
[session.py](file:///c:/code/hiring-pipeline/backend/app/db/session.py)

- 🔴 **No Alembic migrations.** Uses `Base.metadata.create_all()` — destructive in production, can't evolve schema
- 🟡 `get_db` is a synchronous generator in an async application — should use `async_sessionmaker` with `AsyncSession`

#### Security
[security.py](file:///c:/code/hiring-pipeline/backend/app/utils/security.py)

- 🔴 **API key validation is disabled if no keys are configured** — warning log but allows all requests
- 🔴 API keys are validated via simple string comparison, not constant-time comparison (`hmac.compare_digest`) — **timing attack vulnerability**. Ironically, `hmac.compare_digest` IS used in `verify_webhook_signature` but not in `verify_api_key`
- 🔴 **No authentication middleware** — endpoints are completely open. No `Depends()` in any endpoint for auth

#### Main Application
[main.py](file:///c:/code/hiring-pipeline/backend/app/main.py)

- 🔴 `allow_origins=["*"]` — wide-open CORS in production
- 🟡 Uses deprecated `@app.on_event("startup")` instead of FastAPI lifespan

---

### Summary Scorecard

| Pipeline/Component | Data Quality | Error Handling | Persistence | LLM Usage | Modularity | Overall |
|---------------------|:-----------:|:--------------:|:-----------:|:---------:|:----------:|:-------:|
| Blog | 🟡 | 🟡 | 🔴 | 🟡 | 🟢 | 🟡 |
| Career | 🟡 | 🟡 | 🔴 | 🟢 | 🟢 | 🟡 |
| Funding | 🟡 | 🟢 | 🔴 | 🟢 | 🟡 | 🟡 |
| GitHub Issues | 🟡 | 🟡 | 🔴 | 🟡 | 🟢 | 🟡 |
| Hiring Signals | 🟡 | 🟡 | 🔴 | 🟢 | 🟡 | 🟡 |
| Reddit/Market Pain | 🟢 | 🟡 | 🔴 | 🔴 (cost) | 🟢 | 🟡 |
| Pipeline Worker | — | 🟢 | 🟡 | — | 🟡 | 🟡 |
| AI Inference | — | 🔴 | — | 🟡 | 🟢 | 🟡 |
| HTTP/Firecrawl | — | 🔴 | — | — | 🟢 | 🔴 |
| Database/Auth | — | 🟡 | 🔴 | — | 🟡 | 🔴 |

> [!CAUTION]
> **The single biggest systemic issue: None of the 6 pipelines persist their signals to the database.** The models exist (`Signal`, `RawSignal`, `NormalizedSignal`, `FundingEvent`, `HiringSignal`, `GitHubSignal`, `HuggingFaceSignal`, `MarketPain`) but are never written to. All intelligence is generated in-memory and returned in the API response. If the response is lost, all data is gone. This makes the system stateless — there is no historical tracking, no trend analysis, no deduplication across runs.

---

## Part 2: Strategic Gap Analysis

### Project Goal (from [details.md](file:///c:/code/hiring-pipeline/details.md))

> *Build an intelligence system that helps Relanto identify and qualify potential clients by monitoring multiple data sources for signals that indicate a company might need software development services.*

### Key Workflows (stated):
1. Company Analysis — ✅ Exists
2. Market Monitoring — ⚠️ Partially exists (Reddit pipeline runs on-demand, not continuously)
3. Opportunity Scoring — ⚠️ Partially exists (service intelligence does keyword + LLM matching)
4. Outreach Generation — ✅ Exists

---

### Gap Analysis: What's Missing or Needs Upgrading

#### Category A: Data Persistence & Integrity (Critical)

| # | Gap | Impact | Effort |
|---|-----|--------|--------|
| A1 | **Add Alembic migrations** | Without migrations, schema evolution is impossible. `create_all()` is a production antipattern | 🟢 Low |
| A2 | **Persist all signals to database** | Without persistence, there is zero historical data, no trend analysis, no deduplication, and no audit trail. Every pipeline run starts from scratch | 🟡 Medium |
| A3 | **Add deduplication logic** | Same signals get re-discovered on every run. Need fingerprinting/hashing to avoid duplicates | 🟡 Medium |
| A4 | **Add company_id foreign keys** | Signals float as strings with `company_name` — no relational integrity, no join capability | 🟡 Medium |

> [!IMPORTANT]
> **A2 is the highest-priority fix.** The entire value proposition of an "intelligence platform" depends on accumulating and comparing data over time. Without persistence, each analysis is a one-shot throwaway.

---

#### Category B: Missing Pipelines & Data Sources

| # | Gap | Rationale | Effort |
|---|-----|-----------|--------|
| B1 | **LinkedIn Company API** | The most direct signal for hiring, team size, growth rate. Currently relies on Google search which is unreliable | 🟡 Medium |
| B2 | **Crunchbase API integration** | Gold standard for funding data. RSS feed is a stub. Direct API would provide structured funding histories, org charts, investor networks | 🟡 Medium |
| B3 | **News/Press Release monitoring** | Google News API or NewsAPI for press releases, product launches, executive changes. Currently this gap means blog posts are the only content signal | 🟡 Medium |
| B4 | **Stack Overflow/Dev community signals** | Technical pain points from Stack Overflow, dev.to, Hacker News. Currently only Reddit is monitored | 🟡 Medium |
| B5 | **G2/Capterra review monitoring** | Software review platforms reveal deep pain points about specific tools — direct buying signals | 🔴 High |
| B6 | **Company tech stack detection** | Tools like BuiltWith or Wappalyzer API can detect a company's actual tech stack from their website, instead of inferring it from job posts | 🟢 Low |

---

#### Category C: Scoring & Intelligence Quality

| # | Gap | Current State | Proposed Improvement |
|---|-----|---------------|---------------------|
| C1 | **Unified opportunity score** | Service intelligence gives an LLM-generated 1-10 score with no ground truth. Keyword matching is simplistic | Build a weighted multi-factor scoring model: funding recency × hiring velocity × tech pain signals × company size fit. Calibrate with historical win/loss data |
| C2 | **ICP (Ideal Customer Profile) engine** | Relanto's target is hardcoded in [relanto_seed.py](file:///c:/code/hiring-pipeline/backend/app/services/service_intelligence/relanto_seed.py). No configurable ICP | Make ICP configurable: company size range, industries, technologies, funding stage, geographic regions. Score against profile dynamically |
| C3 | **Competitor intelligence** | Zero visibility into what competitors a prospect is evaluating or using | Add competitor mention detection from blog posts, Reddit discussions, and job listings (e.g., "migrating from X to Y") |
| C4 | **Signal freshness weighting** | All signals are treated equally regardless of age. A 6-month-old funding round and yesterday's job post get the same weight | Add temporal decay: recent signals should weigh more in opportunity scoring |
| C5 | **Confidence calibration** | All confidence scores come from LLM self-assessment, which is unreliable | Add source-based confidence: GitHub API data (high confidence) vs. Google search result (low confidence) vs. LLM inference (medium confidence) |

---

#### Category D: Infrastructure & Reliability

| # | Gap | Current State | Proposed Improvement |
|---|-----|---------------|---------------------|
| D1 | **Add retry logic with exponential backoff** | Zero retries on any HTTP call, LLM call, or API call. A single timeout = lost data | Use `tenacity` library for all external calls. Implement per-service rate limiters |
| D2 | **Background job scheduler** | All pipelines run synchronously on API request. No scheduled monitoring | Add Celery/APScheduler/RQ for: scheduled pipeline runs, async processing, retry queues |
| D3 | **Connection pooling** | `httpx.AsyncClient` created per-request. No connection reuse | Create a shared `httpx.AsyncClient` with connection pooling, timeouts, and retry configuration |
| D4 | **LLM cost optimization** | Reddit pipeline makes 5 LLM calls per post. 100 posts = 500 calls. At GPT-4o-mini pricing that's ~$2-5 per run | Batch posts for classification, use cheaper models for filtering, cache LLM responses, use structured output mode |
| D5 | **Implement RSS feed parsing** | RSS fetcher is a stub with TODO comment | Implement with `feedparser` library. This is the cheapest data source and should be working |
| D6 | **OAuth token refresh** | Reddit OAuth token fetched once, never refreshed (1hr expiry) | Implement token refresh logic or use PRAW library which handles this |
| D7 | **Async database sessions** | Sync SQLAlchemy sessions in async FastAPI app | Migrate to `AsyncSession` with `create_async_engine` |

---

#### Category E: UX & Workflow

| # | Gap | Rationale | Effort |
|---|-----|-----------|--------|
| E1 | **Dashboard / Company profiles** | No way to see accumulated intelligence for a company over time. Frontend exists but has limited data to show | 🟡 Medium |
| E2 | **Alert system** | No notifications when high-value signals are detected. BD team has to manually check | 🟡 Medium |
| E3 | **Pipeline status monitoring** | No visibility into which pipelines succeeded/failed, API costs per run, data freshness | 🟢 Low |
| E4 | **Outreach tracking / CRM integration** | `OutreachRecord` model exists with `sent_at`, `opened_at`, `replied_at` fields but no integration with any email or CRM system | 🔴 High |
| E5 | **Company watchlist / monitoring** | No way to set up continuous monitoring for specific companies. Every analysis is ad-hoc | 🟡 Medium |
| E6 | **Export / reporting** | No CSV, PDF, or report generation. Data only available via API | 🟢 Low |

---

#### Category F: Code Quality & Architecture

| # | Issue | Location | Fix |
|---|-------|----------|-----|
| F1 | No authentication on any endpoint | All [endpoints](file:///c:/code/hiring-pipeline/backend/app/api/v1/endpoints) | Add `Depends(verify_api_key)` middleware or FastAPI security scheme |
| F2 | CORS wide open (`*`) | [main.py](file:///c:/code/hiring-pipeline/backend/app/main.py) | Restrict to frontend domain(s) |
| F3 | No input validation schemas on endpoints | [analyze.py](file:///c:/code/hiring-pipeline/backend/app/api/v1/endpoints/analyze.py) — accepts raw `company_name: str` | Use Pydantic request models for all endpoints |
| F4 | No tests | Entire project | Add unit tests for services, integration tests for pipelines |
| F5 | Inconsistent `text=""` pattern in LLM calls | All signal extractors | Refactor `AIInferenceService` to accept a prompt directly without the `{text}` placeholder hack |
| F6 | HuggingFace pipeline not wired | `HuggingFaceService` exists, no pipeline or endpoint calls it | Either wire it into the pipeline worker or remove dead code |
| F7 | `datetime.utcnow()` used everywhere | All models, all services | Use `datetime.now(timezone.utc)` — `utcnow()` is deprecated in Python 3.12+ |
| F8 | f-string logging | All files | Use `logger.info("message %s", var)` lazy formatting for performance |
| F9 | No `__init__.py` exports in services | Various service directories | Add proper exports for cleaner imports |
| F10 | Repository layer is barely used | [repositories/](file:///c:/code/hiring-pipeline/backend/app/repositories) — only 3 files, very thin | Either commit to the repository pattern or remove the layer |

---

### Priority Matrix

```
                    HIGH IMPACT
                        │
           ┌────────────┼────────────┐
           │   A2        │   D2       │
           │ (persist    │ (scheduler)│
           │  signals)   │            │
           │   A1        │   C1       │
  LOW ─────│ (alembic)   │ (scoring)  │───── HIGH
  EFFORT   │   D5        │   B2       │     EFFORT
           │ (RSS fix)   │ (crunchbase│
           │   F1        │   D4       │
           │ (auth)      │ (LLM cost) │
           │   D1        │   E2       │
           │ (retries)   │ (alerts)   │
           └────────────┼────────────┘
                        │
                   LOW IMPACT
```

---

### Recommended Implementation Order

> [!TIP]
> **Phase 1 — Foundation Fixes (1-2 weeks):** Get the basics right before adding features.

1. **A1** — Set up Alembic migrations
2. **A2** — Persist signals to database in every pipeline
3. **A3** — Add signal deduplication (hash-based fingerprinting)
4. **D1** — Add retry logic to HTTP and LLM calls (`tenacity`)
5. **D5** — Implement RSS feed parsing (replace the stub)
6. **F1** — Add API authentication
7. **F7** — Fix `datetime.utcnow()` deprecation

> **Phase 2 — Intelligence Quality (2-3 weeks):** Make the output more valuable.

8. **C1** — Build unified opportunity scoring model
9. **C2** — Make ICP configurable
10. **C4** — Add temporal decay to signal scoring
11. **D4** — Optimize LLM costs (batching, caching, cheaper models for filtering)
12. **D6** — Fix Reddit OAuth token refresh
13. **B6** — Add tech stack detection (BuiltWith/Wappalyzer)

> **Phase 3 — Scale & UX (3-4 weeks):** Make it production-ready.

14. **D2** — Add background job scheduler
15. **E5** — Company watchlist / continuous monitoring
16. **E2** — Alert system for high-value signals
17. **B2** — Crunchbase API integration
18. **B3** — News monitoring pipeline
19. **E1** — Dashboard improvements
20. **F4** — Test suite

---

### Questions for You

> [!IMPORTANT]
> Before I proceed with implementation planning, I need clarity on a few things:

1. **Is this currently in production or still in development?** The answer affects priority (auth & CORS are critical for production, less urgent for dev).

2. **What's the current LLM spend per run?** The Reddit pipeline's 5-calls-per-post pattern could be very expensive. Do you want me to prioritize cost optimization?

3. **Is the frontend actively used?** If the frontend is the primary interface, I should factor in API response shape changes carefully.

4. **Are there any existing companies in the database?** Or is this a fresh start? This affects the migration/persistence strategy.

5. **What's the target: on-demand analysis per company, or continuous monitoring of a watchlist?** This fundamentally changes the architecture (API-driven vs. scheduler-driven).
