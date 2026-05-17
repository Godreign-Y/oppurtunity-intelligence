# Pipeline mapping — PDF steps to implementation

This document maps **REDIT.pdf** phases to Python modules and interfaces. Each stage returns a **Result** type: `Pass(data)` or `Reject(reason_code, detail)`.

## Default configuration (from PDF)

```python
TARGET_SUBREDDITS = [
    "OpenAI", "ClaudeAI", "LocalLLaMA", "MachineLearning",
    "SaaS", "startups", "webdev", "programming",
]

TECH_KEYWORDS = [
    "AI", "API", "tool", "software", "model", "app",
    "platform", "LLM", "plugin", "SaaS",
]

KNOWN_PRODUCTS = {
    "Gemini": "Google",
    "Claude": "Anthropic",
    "Cursor": "Cursor",
    "ChatGPT": "OpenAI",
}

WORKFLOW_PAIN_KEYWORDS = [
    "manually", "workaround", "our company", "production",
    "enterprise", "compliance", "workflow",
]
```

Thresholds (configurable via DB/API):

| Parameter | PDF default | Config key |
|-----------|-------------|------------|
| Min text length | 50 chars | `min_text_length` |
| Min upvotes | 5 | `min_upvotes` |
| Recency window | 30 days | `recency_days` |
| Classifier confidence | > 0.8 | `tech_classifier_min_confidence` |

---

## Phase 1 — Data ingestion

### Step 1 — Connect to Reddit

**Module:** `redit.ingestion.reddit_client`

- Wrap PRAW with app settings from `config`.
- Expose `RedditClient` protocol: `iter_subreddit_posts(name, sort, limit)`.
- Example usage aligned with PDF: `subreddit("OpenAI").hot(limit=100)`.

**Module:** `redit.ingestion.fetcher`

- `PostStream` dataclass: `id`, `subreddit`, `title`, `selftext`, `score`, `created_utc`, `permalink`, optional top comments later.

### Step 2 — Target subreddit selection

**Module:** `redit.ingestion.runner`

- Load active subreddits from `subreddit_targets` table (seeded from defaults).
- For each run: iterate configured list only—never whole Reddit.

**API hook:** `POST /api/v1/ingestion/runs` body `{ "subreddits": optional override, "limit_per_subreddit": 100 }`.

---

## Phase 2 — Stream filtering pipeline

> **Rule:** No DB insert until Phase 5 Step 10.

### Step 3 — Initial metadata filtering

**Module:** `redit.filtering.metadata`

| Check | Logic | Reject code |
|-------|--------|-------------|
| A. Min length | `len(title + body) < min_text_length` | `TOO_SHORT` |
| B. Upvotes | `score < min_upvotes` | `LOW_ENGAGEMENT` |
| C. Recency | `created_utc < now - recency_days` | `STALE` |

Pure Python—no ML.

### Step 4 — Tech relevance (keyword layer)

**Module:** `redit.filtering.tech_keywords`

- Case-insensitive match any `TECH_KEYWORDS` in combined text.
- No match → `Reject(NOT_TECH_KEYWORDS)`.

### Step 5 — Lightweight NLP classifier

**Module:** `redit.filtering.tech_classifier`

**MVP model:** Hugging Face `facebook/bart-large-mnli` zero-shot **or** `cross-encoder/nli-deberta-v3-small` style pipeline with labels:

- Positive: `tech_product_discussion`
- Negative: discard

**Constraints (PDF):** not GPT; run locally; batch size 1 in stream mode.

```python
@dataclass
class TechClassification:
    label: str
    confidence: float
```

Keep iff `label == "tech_product_discussion"` and `confidence > threshold`.

**Reject code:** `LOW_TECH_CONFIDENCE`.

**Note:** Model weights loaded once at app startup (lifespan handler) to avoid per-request cold start.

---

## Phase 3 — Product + business detection

### Step 6 — Product/company extraction

**Module:** `redit.enrichment.products`

**MVP (PDF):**

1. Dictionary lookup `KNOWN_PRODUCTS` (longest match first in text).
2. Optional spaCy `en_core_web_sm` NER for `ORG` / `PRODUCT` as hints—not sole source.

```python
@dataclass
class ProductMatch:
    product: str | None
    company: str | None
    source: Literal["dictionary", "ner", "none"]
```

Posts with no product may still pass if business relevance comes from workflow pain only—policy: **require product OR strong workflow pain** (documented in `intelligence.policy`).

### Step 7 — Business validation

**Module:** `redit.enrichment.business`

**MVP logic:**

- `company` in `KNOWN_PRODUCTS` values or `known_companies` table → pass.
- Unknown product → `Reject(UNKNOWN_BUSINESS)` unless `workflow_pain` pre-score high (config flag).

**Later:** Crunchbase/Clearbit adapters behind `BusinessValidator` interface—no MVP implementation.

---

## Phase 4 — Frustration detection

### Step 8 — Negative sentiment filter

**Module:** `redit.pain.sentiment`

**MVP:** VADER (`vaderSentiment`) on title + body.

```python
@dataclass
class SentimentResult:
    compound: float  # -1 .. 1
    frustration_detected: bool  # compound < -0.3 (tunable)
```

**Reject:** positive/neutral fluff → `NOT_FRUSTRATION`.

**Better (post-MVP):** transformer sentiment behind same interface.

### Step 9 — Workflow/business pain detection

**Module:** `redit.pain.workflow`

- Keyword scan for `WORKFLOW_PAIN_KEYWORDS`.
- Optional regex patterns: `our (team|company)`, `can't deploy`, `in production`.
- Output `workflow_pain_detected: bool` and `business_relevance` score 0–1 (keyword hit count normalized).

Strong workflow signal can compensate weak sentiment in policy layer.

---

## Phase 5 — Store filtered raw JSON

### Step 10 — Raw intelligence JSON

**Module:** `redit.intelligence.builder` + `redit.intelligence.repository`

Build document (matches PDF example + extensions):

```json
{
  "schema_version": "1.0",
  "post_id": "abc123",
  "subreddit": "OpenAI",
  "title": "...",
  "body": "...",
  "upvotes": 142,
  "timestamp": "2026-05-16T12:00:00Z",
  "product": "Gemini",
  "company": "Google",
  "tech_confidence": 0.95,
  "sentiment_score": -0.82,
  "business_relevance": 0.89,
  "workflow_pain_detected": true,
  "permalink": "https://reddit.com/...",
  "ingestion_run_id": "uuid"
}
```

Persist to `intelligence_records` with duplicate protection on `reddit_post_id`.

---

## Orchestrator

**Module:** `redit.pipeline.orchestrator`

```python
async def process_post(post: RawPost, ctx: PipelineContext) -> None:
    for stage in STAGES:
        result = await stage.run(post, ctx)
        if result.is_reject:
            await ctx.rejects.log(post.id, stage.name, result.code)
            return
    record = intelligence_builder.build(post, ctx.accumulated)
    await intelligence_repository.save(record)
```

`STAGES` order is fixed and matches PDF.

## Future: market-gap JSON (beyond PDF)

Not in the 10-page doc but implied by title:

- Cluster intelligence by `(product, pain_theme)`.
- Frequency + sentiment aggregation.
- Export `market_gap.json` — separate module `redit.analytics.clustering` after MVP stores intelligence reliably.
