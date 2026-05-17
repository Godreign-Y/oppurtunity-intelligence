# 🧠 Opportunity Intel — Complete Pipeline Deep Dive

> **What does this system actually answer?**
> *"What technology investments, scaling pressures, and product bets is a company making right now — revealed through their hiring patterns and engineering blog content?"*

---

## ⚡ Quick Overview — What Happens When You Click "Analyze"

```
User types "Airbnb" → clicks Analyze
        ↓
React fires POST /api/v1/analyze
        ↓
FastAPI validates request (Pydantic)
        ↓
asyncio.gather() → runs TWO pipelines IN PARALLEL
    ├── 🏢 Career Pipeline  →  ATS Discovery → Job Extraction → Signal Normalization
    └── 📝 Blog Pipeline    →  Blog Discovery → Firecrawl Scrape → Pain Mapping
        ↓
Merge + Filter (last 30 days) + Sort by confidence
        ↓
Slice to TOP 10 signals only
        ↓
AI Inference (OpenRouter LLM) → structured opportunity assessment
        ↓
Save to SQLite (SQLAlchemy ORM)
        ↓
Return serialized JSON → React renders Signal Cards
```

---

## 🗂️ Phase 1 — Frontend Request Dispatch

**File:** `frontend/src/components/dashboard/AnalyzeForm.tsx`  
**Libraries:** React 18, Axios, Vite (dev proxy)

### What Happens

1. User submits the form → `onSubmit` handler fires
2. React sets `isLoading = true` → spinner appears in the button
3. Axios fires:

```http
POST http://localhost:5174/api/v1/analyze
Content-Type: application/json

{ "company_name": "Airbnb" }
```

4. **Vite Proxy** intercepts this and transparently forwards it to:
```
http://127.0.0.1:8000/api/v1/analyze
```
This is configured in `vite.config.ts` under `server.proxy` — the frontend never talks to port 8000 directly, keeping CORS clean.

5. Axios awaits the response. On success → `setAnalyzeResult(data)`. On error → `setError(...)`.

---

## 🗂️ Phase 2 — FastAPI Endpoint & Concurrent Orchestration

**File:** `backend/app/api/v1/endpoints/analyze.py`  
**Libraries:** FastAPI, Pydantic v2, Python `asyncio`

### Request Validation

Pydantic deserializes the JSON body into:
```python
class AnalyzeCompanyRequest(BaseModel):
    company_name: str = Field(..., description="Name of the company to analyze")
```
If `company_name` is empty or missing, FastAPI auto-returns HTTP 422 before any pipeline runs.

### Concurrent Execution — The Critical Performance Optimization

**Before (sequential — ~40 seconds):**
```python
career_signals = await run_career_pipeline(company_name)  # waits ~20s
blog_signals   = await run_blog_pipeline(company_name)    # then waits ~20s
```

**After (parallel — ~8-10 seconds):**
```python
import asyncio
career_task = run_career_pipeline(company_name)
blog_task   = run_blog_pipeline(company_name)

(career_signals, ats_platform, ats_url), (blog_signals, blog_url) = \
    await asyncio.gather(career_task, blog_task)
```

`asyncio.gather()` submits both coroutines to the event loop simultaneously. Since both are I/O-bound (network calls to external APIs), they run in true parallel without blocking each other.

---

## 🗂️ Phase 3A — Career Intelligence Pipeline

**Files:** `backend/app/services/career/`  
**Libraries:** `httpx` (async HTTP), `re` (Regex), Tavily/Serper APIs

### Step 1 — ATS Discovery (`ats_discovery.py`)

The system doesn't know which job board a company uses. It must discover it.

**Search Query Templates (tried in order):**
```python
ATS_SEARCH_PATTERNS = [
    "{company} career page",
    "site:boards.greenhouse.io {company}",
    "site:jobs.lever.co {company}",
    "site:jobs.ashbyhq.com {company}",
    "site:myworkdayjobs.com {company}",
    "{company} jobs greenhouse",
    "{company} jobs lever",
]
```

Each pattern is fired against the **Serper** (Google Search) or **Tavily** Search API, which returns a list of URLs from search results.

**ATS URL Signature Detection:**
```python
ATS_URL_SIGNATURES = {
    "boards.greenhouse.io":     "greenhouse",
    "boards-api.greenhouse.io": "greenhouse",
    "jobs.lever.co":            "lever",
    "api.lever.co":             "lever",
    "jobs.ashbyhq.com":         "ashby",
    "myworkdayjobs.com":        "workday",
}
```

**Two-Pass URL Matching Logic:**
```python
# Pass 1: Prefer URLs that contain the company slug (most accurate)
company_slug = company_name.lower().replace(" ", "")
for url in urls:
    if company_slug in url.lower():
        for signature, platform in ATS_URL_SIGNATURES.items():
            if signature in url.lower():
                return platform, url   # ✅ High confidence match

# Pass 2: Fallback — any ATS signature match
for url in urls:
    for signature, platform in ATS_URL_SIGNATURES.items():
        if signature in url:
            return platform, url       # ⚠️ Lower confidence match
```

### Step 2 — Slug Extraction (`ats_extractor.py → infer_slug_from_url`)

Once the ATS URL is found, a Regex extracts the company slug:

```python
patterns = {
    "greenhouse": r"boards(?:-api)?\.greenhouse\.io/(?:v1/boards/)?([^/?#]+)",
    "lever":      r"(?:jobs\.lever\.co|api\.lever\.co/v0/postings)/([^/?#]+)",
    "ashby":      r"jobs\.ashbyhq\.com/([^/?#]+)",
    "workday":    r"([\w-]+\.wd\d+\.myworkdayjobs\.com)",
}
```

Example: `https://boards.greenhouse.io/airbnb` → slug = `airbnb`

### Step 3 — Job Data Extraction (ATS-Specific)

**Greenhouse** — Public JSON API (no auth required):
```
GET https://boards-api.greenhouse.io/v1/boards/{slug}/jobs
→ Returns JSON array of job objects with title, departments, offices, updated_at
```

**Lever** — Public JSON API (no auth required):
```
GET https://api.lever.co/v0/postings/{slug}?mode=json
→ Returns JSON array with text, categories{team, location}, createdAt, descriptionPlain
```

**Ashby / Workday** — No public API. Uses **Firecrawl** to scrape the HTML job listing page into Markdown, then parses job titles by looking for lines starting with `#` or capitalized text.

### Step 4 — Signal Extraction (`signal_extractor.py`)

For each raw job dict, the extractor runs:

#### 4a. Technology Detection
```python
tech_keywords = [
    "kubernetes", "k8s", "terraform", "aws", "gcp", "azure",
    "kafka", "redis", "postgresql", "elasticsearch", "docker",
    "grafana", "prometheus", "datadog", "opentelemetry",
    "airflow", "spark", "dbt", "snowflake", "fastapi",
    "python", "typescript", "react", "graphql", "grpc", ...
]
# Exact substring match on lowercased combined text
return [tech for tech in tech_keywords if tech in lower_text]
```

#### 4b. Pain Indicator Detection
```python
CAREER_PAIN_KEYWORD_MAP = {
    "kubernetes":          "infra_scaling",
    "terraform":           "cloud_automation",
    "observability":       "monitoring_gaps",
    "ci/cd":               "deployment_complexity",
    "distributed systems": "scaling_pressure",
    "sre":                 "reliability_pressure",
    "ai engineer":         "ai_initiative",
    "security engineer":   "security_pressure",
    "platform engineer":   "infra_scaling",
    "mlops":               "ai_initiative",
    "data engineer":       "data_scaling",
}
```

Both the job title AND department text are scanned. Pain indicators from both sources are merged and deduplicated.

#### 4c. Seniority Inference
```python
SENIORITY_PATTERNS = [
    (r"\bstaff\b",             "staff"),
    (r"\bprincipal\b",         "principal"),
    (r"\bsenior\b|\bsr\.?\b",  "senior"),
    (r"\bjunior\b|\bjr\.?\b",  "junior"),
    (r"\blead\b",              "lead"),
    (r"\bdirector\b",          "director"),
    (r"\bvp\b|vice president", "vp"),
    (r"\bmanager\b",           "manager"),
]
# Default: "mid" if no match
```

#### 4d. Urgency Tagging
```python
urgency = "Medium"  # default
if any(w in lower_title for w in ["urgent", "immediate", "critical", "staffing", "asap"]):
    urgency = "High"
```

#### 4e. Confidence Scoring
```python
# Greenhouse
confidence = 0.60 + (0.10 if len(technologies) > 2 else 0.0)
# Lever
confidence = 0.62 + (0.10 if len(technologies) > 2 else 0.0)
# Generic (Ashby/Workday)
confidence = 0.55  # fixed — less structured data available
confidence = min(confidence, 0.95)  # hard ceiling
```

---

## 🗂️ Phase 3B — Engineering Blog Pipeline

**Files:** `backend/app/services/blog/`  
**Libraries:** Firecrawl API

### Step 1 — Blog Discovery

Search queries like `"Airbnb engineering blog"` are fired at Serper/Tavily to discover the blog URL. Common patterns recognized: `engineering.{company}.com`, `medium.com/{company}-engineering`, `{company}.tech`.

### Step 2 — Firecrawl Scraping

Firecrawl is an LLM-optimized web scraper. Unlike `requests` or `BeautifulSoup`, it:
- Renders JavaScript (React/Next.js blogs)
- Strips ads and nav chrome
- Returns clean **Markdown** output

```python
# POST https://api.firecrawl.dev/v1/scrape
# Returns: { "markdown": "# Blog Title\n\nContent..." }
```

### Step 3 — Blog Pain Taxonomy Mapping

The Markdown content is scanned against a two-level keyword taxonomy:

```python
BLOG_PAIN_TAXONOMY = {
    "scaling_pressure":       ["scaling", "traffic spike", "sharding", "distributed"],
    "deployment_complexity":  ["deployment", "ci/cd", "pipeline", "rollback", "canary"],
    "cloud_cost_pressure":    ["cost", "spend", "billing", "rightsizing", "spot instances"],
    "reliability_issues":     ["outage", "incident", "latency", "p99", "slo"],
    "legacy_modernization":   ["migration", "rewrite", "monolith", "strangler fig"],
    "ai_adoption_uncertainty":["llm", "genai", "vector database", "embeddings", "mlops"],
    "security_pressure":      ["security", "compliance", "soc2", "gdpr", "zero trust"],
}
```

For each category, **any one keyword match** triggers that pain label on the signal.

---

## 🗂️ Phase 4 — Filtering, Ranking & Prioritization

**Files:** `pipeline.py`, `analyze.py`

### Recency Filter — 30 Day Window
```python
from datetime import datetime, timezone, timedelta
thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

for signal in signals:
    if signal.timestamp:
        ts = signal.timestamp.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(ts)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        if parsed >= thirty_days_ago:
            recent_signals.append(signal)
    else:
        recent_signals.append(signal)  # No timestamp → keep (assume current)
```

### Confidence Sort + Hard Cap
```python
# Sort descending by confidence score
recent_signals.sort(key=lambda x: x.confidence, reverse=True)

# Absolute top-10 cap — no exceptions
top_signals = recent_signals[:10]
```

---

## 🗂️ Phase 5 — AI Inference

**File:** `backend/app/services/ai/inference.py`  
**Libraries:** `openai` SDK (pointed at OpenRouter), model: configurable via `.env`

### Prompt Construction

Rather than dumping raw signal JSON into the LLM (expensive, noisy), the system builds a **compressed analytics summary**:

```python
# Pain indicators sorted by frequency across all signals
pain_counter = {}
for signal in signals:
    for pain in signal.pain_indicators:
        pain_counter[pain] = pain_counter.get(pain, 0) + 1

sorted_pains = sorted(pain_counter.items(), key=lambda x: x[1], reverse=True)
```

The final user prompt sent to the LLM looks like:
```
Company: Airbnb
Total signals analyzed: 10

Top Pain Indicators (by frequency):
  - infra_scaling: 6 occurrence(s)
  - reliability_pressure: 4 occurrence(s)
  - ai_initiative: 3 occurrence(s)

Detected Technologies:
  kubernetes, python, spark, kafka, terraform

Suggested Opportunity Types:
  Infrastructure Scaling Consulting, SRE & Reliability Engineering

Evidence Samples:
  - Job posting: Staff SRE, Infrastructure
  - Job posting: Principal Engineer, ML Platform
```

### LLM Call Configuration
```python
response = await client.chat.completions.create(
    model=settings.llm_model,     # e.g., "deepseek/deepseek-chat"
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_prompt},
    ],
    max_tokens=600,
    temperature=0.2,   # Low temp = deterministic, factual output
)
```

`temperature=0.2` keeps the output grounded and consistent rather than creative.

### Structured Output Enforcement

The system prompt strictly demands JSON-only output:
```json
{
  "detected_opportunity": "Infrastructure Scaling & Reliability Optimization",
  "confidence": 0.85,
  "reasoning": [
    "6 of 10 signals indicate active infra scaling investment",
    "SRE/Platform Engineering roles at principal level signal maturity gap",
    "Kafka + Kubernetes stack signals distributed systems complexity"
  ],
  "recommended_outreach": {
    "stakeholder": "VP of Engineering / CTO",
    "angle": "Position as a reliability & scale partner, not a vendor"
  }
}
```

After receiving the response, any accidental markdown fences are stripped:
```python
clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
data = json.loads(clean)
```

---

## 🗂️ Phase 6 — Database Persistence

**Files:** `company_service.py`, `models/signal.py`  
**Libraries:** SQLAlchemy ORM, SQLite (`dev.db`)

### Signal ORM Model — All Columns
| Column | Type | Purpose |
|---|---|---|
| `id` | UUID (PK) | Unique identifier, auto-generated |
| `company_id` | UUID (FK) | Links to Company table |
| `source_type` | String | `"career_page"` or `"engineering_blog"` |
| `event_type` | String | `"hiring_signal"` |
| `technologies` | JSON | List of detected tech strings |
| `pain_indicators` | JSON | List of pain category strings |
| `opportunity_mapping` | JSON | List of suggested opportunity types |
| `confidence` | Float | 0.0 – 0.95 scoring |
| `role_title` | String | Raw job title |
| `department` | String | Department name |
| `seniority` | String | Inferred seniority level |
| `location` | String | Office or "Remote" |
| `urgency` | String | `"High"` or `"Medium"` |
| `timestamp` | DateTime | Original posting date (parsed from ISO string) |
| `created_at` | DateTime | DB insert time |

### Critical Type Conversion
SQLite's `DateTime` column **rejects** Python strings. The timestamp must be parsed before insertion:
```python
timestamp=datetime.fromisoformat(
    s.timestamp.replace("Z", "+00:00")
) if s.timestamp else None
```

### Serialization Back to Frontend

After committing to DB, the ORM objects are validated through Pydantic:
```python
SignalResponse.model_validate(orm_obj).model_dump(mode="json")
```

This ensures the response includes the DB-generated `id` (UUID), which the frontend requires for the signal detail deep-dive view.

---

## 🗂️ Phase 7 — Frontend Rendering

**Files:** `AnalysisResult.tsx`, `SignalCard.tsx`, `SignalDetail.tsx`

### Signal Cards — Computed Display Logic
```typescript
// Relative time from timestamp
function getRelativeTime(timestamp?: string | null) {
  const diff = Date.now() - new Date(timestamp).getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  return `${days} days ago`;
}

// Urgency badge
{signal.urgency === 'High' && (
  <span className="bg-red-500 text-white text-[10px] uppercase font-bold rounded">
    Urgent
  </span>
)}
```

### Sidebar — Past Analyses
Clicking a tracked company in the left sidebar fires:
```http
GET /api/v1/companies/{company_name}/signals
```
This returns all persisted signals for that company from the DB, enabling instant re-inspection without re-running the full pipeline.

---

## 🛠️ Complete Technology Reference

### Backend
| Technology | Version | Role |
|---|---|---|
| **FastAPI** | 0.100+ | Async REST API framework |
| **Pydantic v2** | 2.x | Request/response validation & serialization |
| **SQLAlchemy** | 2.x | ORM for DB operations |
| **SQLite** | — | Local development database (`dev.db`) |
| **httpx** | 0.25+ | Async HTTP client for ATS API calls |
| **asyncio** | stdlib | Concurrent pipeline execution |
| **uvicorn** | — | ASGI server |

### Frontend
| Technology | Version | Role |
|---|---|---|
| **React** | 18 | UI framework |
| **Vite** | 5.x | Build tool + dev proxy |
| **TypeScript** | 5.x | Type-safe component development |
| **Axios** | 1.x | HTTP client |
| **Lucide React** | — | Icon system |
| **TailwindCSS** | 3.x | Utility-first styling |

### External APIs
| API | Purpose | Auth |
|---|---|---|
| **Serper** | Google Search programmatic access | `SERPER_API_KEY` |
| **Tavily** | AI-native search with structured results | `TAVILY_API_KEY` |
| **Firecrawl** | LLM-native web scraping to Markdown | `FIRECRAWL_API_KEY` |
| **OpenRouter** | LLM gateway (DeepSeek, Llama3, etc.) | `OPENROUTER_API_KEY` |
| **Greenhouse API** | Public job board data (no auth) | None |
| **Lever API** | Public job board data (no auth) | None |

---

## 🔑 Key Design Decisions Explained

| Decision | Why |
|---|---|
| `asyncio.gather()` for both pipelines | Cuts 40s sequential time to ~10s parallel |
| Top 10 hard cap | Signal-to-noise ratio — 200 signals is overwhelming, 10 is actionable |
| 30-day recency filter | Stale jobs indicate past priorities, not current bets |
| Confidence scoring per source | Greenhouse (0.60+) > Lever (0.62+) > Generic (0.55) reflects data richness |
| Two-pass ATS URL matching | Slug-match first prevents false positives on unrelated company URLs |
| `temperature=0.2` for LLM | Deterministic, grounded output over creative fabrication |
| ORM → Pydantic serialization | Ensures DB-generated UUIDs propagate to frontend for deep-link navigation |
