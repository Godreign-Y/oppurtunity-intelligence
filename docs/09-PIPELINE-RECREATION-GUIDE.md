# REDIT Pipeline Recreation Guide

This document explains the logical approach behind the current REDIT pipeline so
the idea can be recreated in another codebase, language, platform, or production
system.

The core idea is:

> Convert noisy Reddit posts into validated, business-facing market intelligence
> by applying cheap filters first, semantic filters second, canonicalization
> third, and clustering/aggregation last.

The current implementation is a useful prototype. It contains several strong
design choices worth copying, and several operational gaps that should be fixed
before rebuilding it professionally.

## Overall Pipeline

At a high level, the system does the following:

1. Discover Reddit posts from multiple sources.
2. Normalize each Reddit item into one internal post schema.
3. Deduplicate posts across feeds, subreddits, and searches.
4. Run lightweight metadata filters.
5. Run semantic technology relevance filtering.
6. Extract product/company hints.
7. Detect frustration or pain signals.
8. Detect workflow/business relevance.
9. Validate whether the post is commercially meaningful.
10. Canonicalize the noisy post into a stable business problem statement.
11. Build a structured intelligence record.
12. Generate embeddings for the canonical problem.
13. Persist only validated intelligence, not the entire raw Reddit stream.
14. Cluster validated records into repeated pain themes.
15. Aggregate clusters into final business intelligence opportunities.
16. Expose run summaries and intelligence through an API.

Conceptually, the system is not a scraper. It is a staged signal extraction
pipeline. The purpose is not to collect a large volume of Reddit data. The
purpose is to identify repeated, commercially meaningful pain points that may
indicate unmet demand, weak incumbents, workflow gaps, or product opportunities.

## Mental Model

The pipeline has three layers:

1. Input discovery
2. Per-post validation
3. Cross-post intelligence synthesis

Input discovery answers:

- Where do candidate posts come from?
- How do we avoid fetching only from biased or narrow communities?
- How do we avoid duplicate posts?

Per-post validation answers:

- Is this post recent enough?
- Is it long enough to contain usable signal?
- Is it about technology, software, tools, platforms, or workflows?
- Is there frustration, inefficiency, complexity, or unmet need?
- Is the pain business-relevant rather than purely casual or personal?
- Can it be normalized into a clean intelligence record?

Cross-post synthesis answers:

- Are many validated posts describing the same underlying pain?
- Which pain themes have the strongest combination of frequency, frustration,
  and commercial relevance?
- Which tools, platforms, companies, personas, and workflows are repeatedly
  involved?

This separation is important. A single Reddit post is weak evidence. A cluster
of independently discovered, semantically similar complaints is much stronger
market evidence.

## Step 1: Reddit Discovery

### Current Approach

The system supports multiple discovery inputs:

- Global feeds such as `r/all` and `r/popular`
- Specific subreddit feeds
- Reddit search queries

The current public JSON source fetches from endpoints such as:

- `/r/all/{sort}.json`
- `/r/popular/{sort}.json`
- `/r/{subreddit}/{sort}.json`
- `/search.json?q=...`

Pagination uses Reddit's `after` cursor. The source yields posts as an async
stream rather than downloading everything upfront.

### Logical Purpose

Discovery should maximize recall without turning the rest of the system into a
garbage collector.

The system wants broad exposure to possible pain signals. If discovery is too
narrow, the pipeline will only reflect the assumptions of the initial subreddit
list. If discovery is too broad without strong downstream filters, the system
will waste compute on unrelated posts.

A good discovery strategy should combine:

- Broad feeds for unexpected signals
- Targeted subreddits for domain-specific depth
- Search queries for direct intent capture
- Historical re-runs for trend tracking

### Good Things Worth Copying

- The source interface is swappable. Public JSON can later be replaced by PRAW,
  Reddit API credentials, a data vendor, or another community source.
- Discovery is streamed. This avoids holding a large raw batch in memory.
- Multiple source types are merged into one normalized stream.
- Deduplication happens early by Reddit post id.

### Make It Better

Use an explicit discovery plan object per run:

```json
{
  "feeds": ["all", "popular"],
  "subreddits": ["devops", "kubernetes", "programming"],
  "search_queries": ["terraform deployment pain", "github actions failing"],
  "sort": "new",
  "limit_per_source": 100,
  "time_window_days": 30
}
```

This makes runs reproducible. A professional system should store the discovery
plan, source counts, request failures, rate-limit events, and cursor metadata.

Also separate "configured defaults" from "request overrides". In the current
code, defaults exist in settings, but request handling does not fully express a
clean discovery policy.

### Edge Cases

- Reddit posts can be deleted or removed after discovery.
- Public JSON endpoints can return rate limits, 403s, 429s, or empty pages.
- Some subreddits block unauthenticated access.
- Search results can be low quality or heavily duplicated.
- `r/all` and `r/popular` are noisy and can overrepresent viral posts.
- Sorting by `new` improves freshness but increases low-signal content.
- Sorting by `top` improves engagement but misses early market signals.

Professional handling should include retries with backoff, per-source failure
isolation, source-level metrics, and partial-run completion instead of failing an
entire run because one source broke.

## Step 2: Normalize Reddit Posts

### Current Approach

Every Reddit listing is converted into a `RawRedditPost`-style internal schema:

- id
- subreddit
- title
- body
- score
- created timestamp
- permalink
- URL
- author
- comment count

The rest of the pipeline only works with this internal shape.

### Logical Purpose

Normalization isolates the pipeline from source-specific quirks. Reddit JSON,
PRAW, imported CSVs, Hacker News, Discord exports, GitHub issues, and support
tickets could all map into a common "raw candidate signal" model.

This is a strong abstraction. It means the intelligence pipeline is not tied to
Reddit forever.

### Good Things Worth Copying

- Normalize early.
- Keep source-specific parsing outside the filter stages.
- Use a combined text property from title plus body for downstream scoring.
- Store source identifiers such as post id and permalink for traceability.

### Make It Better

Add a richer source metadata block:

```json
{
  "source_type": "reddit",
  "source_name": "r/devops",
  "source_query": "terraform state locking",
  "source_sort": "new",
  "fetched_at": "2026-05-17T08:00:00Z",
  "raw_external_id": "t3_abc123"
}
```

Also preserve raw payloads selectively. The current idea of not storing all raw
posts is good for reducing data risk, but in production you usually want either:

- no raw body storage, only validated records, or
- short-lived raw storage with retention, audit controls, and deletion support.

The right choice depends on privacy, compliance, and debugging needs.

## Step 3: Deduplication

### Current Approach

The discovery stream keeps a `seen_ids` set and skips posts already yielded from
another source.

### Logical Purpose

The same post can appear in `r/all`, `r/popular`, a subreddit feed, and search
results. Without deduplication, a single viral post may look like repeated
market demand.

Deduplication protects both compute cost and analytical integrity.

### Good Things Worth Copying

- Deduplicate before expensive ML.
- Deduplicate by stable external id when available.
- Treat deduplication as part of ingestion, not as a later analytics cleanup.

### Make It Better

Use two levels of deduplication:

1. Exact source id deduplication
2. Near-duplicate text deduplication

Near duplicates matter because users repost the same complaint, cross-post
between subreddits, or quote the same issue. Use normalized text hashing,
MinHash, SimHash, or embedding similarity to detect repeated copies.

Also persist deduplication state across runs. Current in-memory deduplication
only protects one run. A production system should avoid reprocessing the same
post across daily runs unless explicitly requested.

## Step 4: Metadata Filtering

### Current Approach

The metadata filter rejects:

- Empty, deleted, or removed posts
- Posts with text shorter than the configured minimum
- Heavily downvoted posts
- Posts older than the configured recency window

The implementation intentionally avoids aggressive upvote filtering to preserve
recall for fresh or niche pain points.

### Logical Purpose

Metadata filtering is a cheap first gate. It removes obviously unusable inputs
before the system spends model inference, LLM calls, embedding generation, or
database writes.

This stage should be deterministic, explainable, and fast.

### Good Things Worth Copying

- Cheap filters run before expensive semantic filters.
- Rejects include stage and reason code.
- Engagement filtering is conservative, which is good for early signal
  detection.
- Recency is configurable.

### Make It Better

Make metadata policy explicitly configurable per run or per workspace:

```json
{
  "min_text_length": 50,
  "max_text_length": 8000,
  "recency_days": 30,
  "minimum_score": -5,
  "allow_nsfw": false,
  "allow_deleted_author": true
}
```

Consider adding:

- Language detection
- Spam/link-farm detection
- Bot-author heuristics
- Removed/deleted body detection
- Duplicate title detection
- Extremely long text truncation policy

### Edge Cases

- Short posts can still contain strong market signal: "Datadog pricing is
  killing us."
- Very new posts often have low or zero score.
- Old posts can be useful for longitudinal trend analysis.
- Highly downvoted posts can still describe real pain, especially in fan
  communities.

For production, track rejected counts by reason. If too many posts are rejected
as too short or stale, operators need visibility to tune thresholds.

## Step 5: Semantic Technology Relevance

### Current Approach

The system uses a sentence-transformer model and compares the post text against
pre-encoded anchor phrases:

- Technology/product anchors
- Non-technology anchors

It computes:

- maximum tech similarity
- maximum non-tech similarity
- margin between the two

The post passes if tech similarity and margin exceed configured thresholds.

### Logical Purpose

Keyword filters are brittle. A post can discuss software pain without saying
obvious words like "API" or "SaaS". Conversely, a post can mention "AI" in a
joke or unrelated meme.

Semantic relevance scoring catches broader meaning while still being cheaper
than an LLM call.

### Good Things Worth Copying

- Use embedding anchors as a lightweight semantic classifier.
- Pre-encode anchors once at startup.
- Compare against negative anchors, not only positive anchors.
- Use both absolute similarity and positive-vs-negative margin.
- Run model inference off the event loop when inside an async API.

### Make It Better

Use a calibrated classifier or retrieval/reranking stack:

1. Anchor-similarity gate for fast recall.
2. Lightweight cross-encoder or small classifier for precision.
3. Optional LLM adjudication only for borderline cases.

Keep a labeled evaluation set. Thresholds such as `0.32` similarity or `0.05`
margin are not universally meaningful. They should be tuned against examples:

- true technology pain
- technology news but no pain
- casual product discussion
- memes and jokes
- career advice
- consumer complaints
- enterprise workflow pain

### Edge Cases

- Product names can be ambiguous: "Cursor", "Claude", "Gemini", "Copilot".
- Posts about career frustration can look similar to tool frustration.
- News articles can mention technology heavily but not contain user pain.
- Consumer app complaints may not be relevant to B2B opportunity discovery.

Professional setups should store the score, margin, anchor version, model
version, and threshold version for every accepted record.

## Step 6: Product and Company Extraction

### Current Approach

The implementation uses a dictionary of known products mapped to companies. It
does longest-match-first string matching against the post text.

Examples:

- ChatGPT -> OpenAI
- Claude -> Anthropic
- AWS -> Amazon
- GitHub Copilot -> Microsoft
- Datadog -> Datadog

This stage enriches the post. It does not reject by itself.

### Logical Purpose

Product/company extraction connects raw complaints to markets and vendors.

This helps answer:

- Which tools are repeatedly causing pain?
- Which companies are affected by the pain?
- Is the complaint about a real product category?
- Are there incumbent weaknesses that suggest an opportunity?

### Good Things Worth Copying

- Product extraction is enrichment-only.
- Business validation is kept as a separate stage.
- Longest-match-first avoids simple collisions such as matching "Copilot"
  before "GitHub Copilot".

### Make It Better

A production extractor should combine:

- Dictionary lookup
- Alias tables
- Product taxonomy
- Named entity recognition
- LLM structured extraction with schema validation
- Confidence scoring
- Human-reviewable unknown entity queue

Use a normalized entity table:

```json
{
  "canonical_name": "GitHub Actions",
  "entity_type": "product",
  "vendor": "Microsoft",
  "aliases": ["GHA", "GitHub CI", "Actions"],
  "categories": ["CI/CD", "Developer Tools"],
  "confidence": 0.94
}
```

### Edge Cases

- Product names overlap with common words.
- Multiple products can appear in one post.
- The complained-about product may not be the product causing the pain.
- A post may describe a workflow problem without naming a vendor.
- Open source projects may not map cleanly to companies.
- Vendor inference can be wrong: Kubernetes is not always "Google" in a
  commercially meaningful sense.

For professional use, model entities as many-to-many relationships with roles:

- complained_about
- used_with
- alternative_considered
- vendor_ecosystem
- integration_dependency

## Step 7: Frustration Detection

### Current Approach

The current branch uses zero-shot classification with labels such as:

- developer frustration
- workflow pain
- tooling annoyance
- operational inefficiency
- infrastructure complexity
- positive discussion

The post passes if the top label is one of the pain labels and exceeds the
threshold.

### Logical Purpose

Technology relevance alone is not enough. The system is looking for pain,
friction, unmet need, complexity, delays, inefficiency, and negative operational
impact.

Frustration detection separates:

- "How do I use Terraform?"
- "Terraform state locking blocked our deployment again."

The second is more useful for opportunity discovery.

### Good Things Worth Copying

- Frustration is treated as semantic classification, not only sentiment.
- Labels include operational pain, not just emotional negativity.
- The score is preserved for later business scoring.

### Make It Better

Use a more domain-specific pain classifier. Generic zero-shot labels can be slow
and unstable. Better options:

- Fine-tune a small classifier on labeled pain/non-pain posts.
- Use a cross-encoder for pain relevance.
- Use LLM labeling offline to create training data.
- Split pain into dimensions:
  - severity
  - urgency
  - workaround present
  - business impact
  - repeated occurrence
  - willingness to pay

Also distinguish:

- emotional frustration
- operational pain
- product defect
- pricing complaint
- integration gap
- documentation confusion
- security/compliance blocker

Each category has different business implications.

### Edge Cases

- Sarcasm is hard.
- "This is killing me" may be metaphorical but useful.
- Highly technical posts may express pain without emotional language.
- Some complaints are user error, not market opportunity.
- Some posts are outrage without a solvable product gap.

Professional systems should include calibration and periodic manual review of
false positives and false negatives.

## Step 8: Workflow and Business Pain Detection

### Current Approach

The workflow scorer uses sentence-transformer embeddings against workflow pain
anchors and negative anchors. It returns:

- relevance score
- detected boolean
- positive similarity
- negative similarity

The current workflow filter always passes and adds metadata. Business validation
later decides whether the signal is enough.

### Logical Purpose

The system cares especially about pains with business context:

- manual workarounds
- deployment delays
- production incidents
- team inefficiency
- compliance blockers
- operational overhead
- repeated debugging

This stage converts general frustration into commercial relevance.

### Good Things Worth Copying

- Workflow/business relevance is separate from generic frustration.
- Semantic anchors are better than pure keyword matching.
- The stage enriches context instead of rejecting too early.

### Make It Better

Make business relevance multi-factor:

```json
{
  "team_context": true,
  "production_context": true,
  "manual_workaround": true,
  "time_cost": "high",
  "repetition": "weekly",
  "buyer_persona_present": true,
  "business_relevance_score": 0.82
}
```

Consider explicit detectors for:

- "our team", "at work", "in production"
- time wasted
- money wasted
- compliance/security blockers
- customer impact
- manual repetitive work
- failed existing tools
- migration intent
- asking for alternatives

### Edge Cases

- Hobbyist pain can look like business pain.
- Enterprise language can appear in generic news articles.
- Workflow pain can be strong even when no company is named.
- Pricing complaints can indicate willingness to pay or churn risk, depending on
  context.

Professional scoring should separate confidence from severity. A very confident
minor annoyance should not outrank a lower-confidence but severe production
blocker without review.

## Step 9: Business Validation

### Current Approach

A post passes business validation if:

- a known product or known company was found, or
- workflow pain was detected, or
- business relevance exceeds the configured minimum

Otherwise it is rejected as `UNKNOWN_BUSINESS`.

### Logical Purpose

This stage asks whether the post is likely to matter commercially. It protects
the system from producing intelligence on generic emotional posts or irrelevant
technical chatter.

Business validation is a policy stage. It combines the signals produced earlier.

### Good Things Worth Copying

- Keep business validation after product, frustration, and workflow scoring.
- Allow workflow pain to pass even without a known product.
- Use explicit reject reasons.

### Make It Better

Make validation policy declarative and versioned:

```json
{
  "policy_version": "2026-05-17",
  "pass_if": [
    "known_product AND frustration_score >= 0.55",
    "workflow_relevance >= 0.45 AND business_context = true",
    "production_impact = true",
    "manual_workaround = true AND repetition = true"
  ]
}
```

This lets operators change policy without code deploys and compare policy
versions across runs.

### Edge Cases

- A brand-new product will not exist in the dictionary.
- A category-level pain can be valuable without product names.
- Product mentions can be incidental.
- "Which tool should I use?" may signal demand but not pain.

Professional systems should keep borderline cases in a review queue instead of
hard rejecting them forever.

## Step 10: Canonicalization

### Current Approach

The canonicalization stage calls an LLM through Groq and asks it to convert noisy
Reddit text into a stable business-facing schema:

- problem statement
- pain category
- affected tools
- affected platforms
- affected persona
- business impact
- urgency
- solution category
- possible companies affected
- raw title/body

The prompt strongly instructs the model to produce consistent wording. For
example:

`Terraform state management causing deployment delays`

instead of:

`DevOps nightmare`

If canonicalization fails, the code falls back to a simpler title-based
canonical problem.

### Logical Purpose

Canonicalization is the bridge between noisy social text and useful analytics.

Users describe the same problem in many ways:

- "GitHub Actions failed again"
- "CI broke our deploy"
- "Our release pipeline is flaky"
- "Actions randomly dies during prod deploys"

If each post is embedded as raw text, clustering can scatter similar problems.
Canonicalization reduces semantic variance before embedding and clustering.

### Good Things Worth Copying

- Canonicalization happens after filtering, so LLM cost is spent only on likely
  valuable posts.
- The prompt optimizes for stable, short, business-facing wording.
- The schema is explicit.
- There is a fallback path.

### Make It Better

Use structured outputs with strict schema validation and retries. Also store:

- prompt version
- model name
- canonicalization confidence
- fallback flag
- raw extraction errors
- token/cost metadata

Add deterministic post-processing:

- normalize tool names
- normalize company names
- enforce allowed category taxonomy
- enforce urgency enum
- strip unsupported claims
- prevent hallucinated vendors

For high-value systems, canonicalization should be evaluated. Build a golden
dataset of raw posts and expected canonical records.

### Edge Cases

- LLMs can hallucinate companies or tools.
- Fallback based only on title may produce weak intelligence.
- Posts can contain multiple distinct pains.
- Posts can complain about one tool while mentioning several others.
- Canonicalizing too aggressively can merge different problems.
- Canonicalizing too loosely can fragment one problem into many clusters.

Professional setups should support one-to-many extraction when a post contains
multiple separable pain points.

## Step 11: Intelligence Record Building

### Current Approach

The intelligence builder combines:

- normalized Reddit post
- accumulated filter metadata
- canonicalization output
- run id

It produces a structured `IntelligenceRecord`.

The record includes:

- post metadata
- product/company
- tech confidence
- frustration score
- business relevance
- workflow pain flag
- canonical problem statement
- pain category
- affected tools/platforms
- business impact
- urgency
- solution category
- matched keywords

### Logical Purpose

This is the first durable output of the pipeline. Everything before this is
candidate processing. The intelligence record is the validated, queryable unit of
market signal.

### Good Things Worth Copying

- Build a versioned output schema.
- Include source traceability through post id and permalink.
- Store the scores that justified the decision.
- Keep canonical business fields separate from raw title/body.

### Make It Better

The record should include:

- run id as a real database column
- source metadata
- model versions
- policy versions
- stage-by-stage decision trace
- confidence scores per extracted field
- canonicalization fallback indicator
- raw text hash
- deduplication group id

Also fix field propagation. In the current code, `possible_companies_affected`
is extracted during canonicalization but not passed through the builder, so it
defaults to an empty list in the final record.

### Edge Cases

- Some fields are unknown but the record is still useful.
- Scores from different models are not automatically comparable.
- A record can pass due to workflow pain even without a product.
- Raw body may contain personal data; retention policy matters.

Professional systems should define what fields are required for each downstream
use case. Do not require unnecessary fields if doing so causes valuable signals
to be dropped.

## Step 12: Embedding Generation

### Current Approach

The system generates embeddings from:

`problem_statement | pain_category`

using `all-MiniLM-L6-v2`, normalized embeddings, and a fixed vector dimension.

Embeddings are stored with canonical intelligence records for clustering.

### Logical Purpose

Embeddings convert canonical problem statements into vectors so the system can
find recurring themes across posts.

Using canonical text instead of raw Reddit text is important because raw posts
contain jokes, tangents, code snippets, long stories, and unrelated context.

### Good Things Worth Copying

- Embed the canonical problem, not only the raw post.
- Normalize embeddings for similarity operations.
- Store embeddings with the intelligence record.

### Make It Better

Do not instantiate another sentence-transformer model if one is already loaded
in the application registry. The current pipeline loads a shared transformer for
some stages, then `EmbeddingService` loads its own model again. A professional
system should share model instances or use a dedicated embedding worker.

Also store:

- embedding model name
- embedding model version
- input text used for embedding
- vector dimension
- creation timestamp

Consider embedding multiple views:

- canonical problem statement
- full canonical record
- raw title/body
- tool/category-specific text

Different views can support different analytics.

### Edge Cases

- Short canonical statements may lose nuance.
- Long raw posts may introduce noise.
- Upgrading embedding models invalidates old vector distances.
- Mixed embedding versions in one clustering run can corrupt results.

Professional systems should re-embed in controlled migrations and avoid mixing
model versions in the same cluster job.

## Step 13: Persistence

### Current Approach

The FastAPI app initializes an in-memory run store for API retrieval, but the
ingestion path also writes canonical intelligence and final aggregation records
to a Postgres/pgvector database.

The code comments indicate an intended optimization:

- use one database session for the full ingestion lifecycle
- flush individual records
- commit once at the end

### Logical Purpose

The right persistence principle is:

> Do not store everything. Store validated intelligence plus enough traceability
> to audit why it was accepted.

This reduces storage, noise, privacy risk, and downstream analytical burden.

### Good Things Worth Copying

- Store only high-signal validated records.
- Use database uniqueness on external post id.
- Generate embeddings during persistence so validated records are cluster-ready.
- Prefer batching and flushing over per-record commits.

### Make It Better

The current implementation needs cleanup:

- It says in-memory in the README, but imports database code at startup.
- It has no included Alembic migration files.
- Some repository methods call `commit()` internally, breaking the intended
  single-transaction behavior.
- Canonical records do not include `run_id`, making run-scoped aggregation hard.

Professional setup should use:

- Alembic migrations committed to the repo
- explicit transaction ownership at service/job level
- no commits inside repositories unless the repository owns the transaction
- run id foreign keys
- idempotent upserts
- reject logs
- schema versioning
- migration tests

### Edge Cases

- Duplicate post insert can fail due to unique constraint.
- One bad record can roll back an entire run unless handled carefully.
- Long transactions can be risky for large runs.
- Partial commits can leave inconsistent aggregation output.
- API reads from memory will not show DB-persisted records after restart.

A professional design should choose one source of truth. Either API reads from
database, or the system is explicitly ephemeral. Mixing both creates confusing
behavior.

## Step 14: Clustering

### Current Approach

The clustering orchestrator:

1. Fetches all canonical records with embeddings.
2. Converts embeddings into a NumPy array.
3. Runs UMAP dimensionality reduction.
4. Runs HDBSCAN clustering.
5. Builds in-memory cluster analysis objects.

The current service uses:

- UMAP `n_neighbors=15`
- UMAP `n_components=10`
- HDBSCAN `min_cluster_size=5`

### Logical Purpose

Clustering turns individual validated posts into repeated market themes.

This is the key step that converts anecdotal complaints into stronger evidence.
One post is a signal. A cluster of similar complaints is a possible market gap.

### Good Things Worth Copying

- Use density-based clustering so noise points can remain unclustered.
- Cluster after canonicalization and embedding.
- Treat cluster analysis as a separate phase from per-post validation.
- Do not force every post into a cluster.

### Make It Better

The current clustering path has an important small-run bug. The orchestrator
allows clustering with 5 records, but UMAP is configured with 10 output
components. In local testing, 5 and 11 records crashed in UMAP. Twelve records
ran but produced all noise.

A professional clustering job should dynamically adapt:

```python
n_records = len(records)
n_neighbors = min(configured_neighbors, n_records - 1)
n_components = min(configured_components, n_records - 2)
min_cluster_size = min(configured_min_cluster_size, max(2, n_records // 3))
```

It should also skip clustering until the dataset is large enough to produce a
meaningful result. For many use cases, fewer than 25-50 validated records is too
small for stable unsupervised clustering.

Also cluster per run or per analysis window. The current repository fetches all
historical canonical records, not only the current run. That may be useful for
global clustering, but it is not correct if the API response implies run-specific
intelligence.

### Edge Cases

- Small datasets can crash UMAP or produce meaningless clusters.
- HDBSCAN may label everything as noise.
- Similar wording from canonicalization can over-merge distinct issues.
- Different embedding model versions can distort clusters.
- Very large clusters may contain subthemes that need secondary clustering.
- New records may need incremental clustering rather than full reclustering.

Professional alternatives:

- Skip UMAP for small datasets and cluster directly in embedding space.
- Use agglomerative clustering with a distance threshold for smaller sets.
- Use HDBSCAN only above a minimum record count.
- Run topic modeling or BERTopic-style analysis on larger corpora.
- Use approximate nearest neighbor indexes to find recurring themes.
- Add human review for high-value clusters.

## Step 15: Aggregation Into Business Intelligence

### Current Approach

The aggregation service converts each cluster into a final intelligence record.
It computes:

- cluster size
- average frustration score
- average business relevance
- normalized size
- business score from a weighted formula
- representative problem statement
- affected tools
- possible companies affected
- precise description

Business score formula:

```text
business_score =
  (
    avg_relevance * 0.5
    + avg_frustration * 0.3
    + normalized_cluster_size * 0.2
  ) * 10
```

### Logical Purpose

Aggregation converts clusters into decision-friendly opportunity records.

Raw clusters are not enough. A product, strategy, or investment user wants:

- what problem is recurring?
- how many posts support it?
- how frustrated are users?
- what tools/platforms are involved?
- which companies or categories are implicated?
- how commercially interesting is the theme?

### Good Things Worth Copying

- Business scoring combines intensity and frequency.
- The representative problem is chosen from canonical statements.
- Affected tools and companies are aggregated across supporting records.
- Final intelligence is separate from raw per-post intelligence.

### Make It Better

The current scoring is a reasonable prototype, but professional scoring should
be more nuanced:

```text
opportunity_score =
  severity_weight
  + recurrence_weight
  + business_context_weight
  + buyer_persona_weight
  + workaround_weight
  + market_gap_weight
  - noise_penalty
  - ambiguity_penalty
```

Additional useful signals:

- number of distinct subreddits
- number of distinct authors
- time spread of complaints
- growth trend over time
- presence of "looking for alternatives"
- manual workaround mentions
- production/customer impact
- pricing sensitivity
- competitor mentions
- repeated tool combinations
- cluster coherence score
- support from comments, not only posts

Also store supporting post ids. A final intelligence record without evidence is
hard to audit.

### Edge Cases

- A cluster can be large because of a single viral topic, not recurring demand.
- A small cluster can be commercially valuable if the pain is severe and
  enterprise-specific.
- Average frustration can hide polarized records.
- A repeated complaint may indicate a known product category with many existing
  solutions, not a new opportunity.
- Company inference can accidentally imply causation when it only indicates
  ecosystem association.

Professional output should include both a score and an explanation of why the
score was assigned.

## Step 16: API and Run Reporting

### Current Approach

The API exposes:

- `POST /api/v1/ingestion`
- `GET /api/v1/intelligence/{run_id}`

The run summary includes:

- run id
- status
- sources
- fetched count
- passed count
- rejected count
- reject counts by stage
- start/end time
- error message

### Logical Purpose

Operators need to trigger runs, inspect whether runs worked, and retrieve the
validated intelligence output.

Run reporting is not just a UI feature. It is how threshold tuning, data quality
debugging, and model evaluation become possible.

### Good Things Worth Copying

- Include reject counts by stage.
- Return run ids.
- Keep API surface small while the core pipeline is evolving.
- Expose export-friendly intelligence JSON.

### Make It Better

Use asynchronous jobs for ingestion. A long-running Reddit/ML/LLM pipeline
should not execute fully inside one HTTP request.

Professional shape:

- `POST /runs` creates a queued job.
- Worker processes the run.
- `GET /runs/{id}` returns status and metrics.
- `GET /runs/{id}/records` returns accepted intelligence.
- `GET /runs/{id}/rejects` returns sampled reject diagnostics.
- `GET /opportunities` returns aggregated intelligence.

Add progress reporting:

```json
{
  "status": "running",
  "sources_done": 3,
  "sources_total": 7,
  "posts_fetched": 942,
  "posts_processed": 920,
  "posts_passed": 38,
  "current_stage": "canonicalization"
}
```

### Edge Cases

- Runs can exceed HTTP timeouts.
- Model downloads can delay first startup.
- LLM APIs can fail mid-run.
- Database writes can fail after expensive processing.
- Users may trigger overlapping runs.

Use a job queue, idempotency keys, cancellation support, run locking, and
operator-visible logs.

## What To Copy

These are the strongest ideas in the current pipeline:

1. Stream-first processing

Process posts one at a time instead of bulk-storing everything. This limits
noise, cost, and storage burden.

2. Ordered cheap-to-expensive filtering

Metadata filters come before embeddings, classifiers, LLM calls, and clustering.
This is the correct cost shape.

3. Normalized internal post schema

Source-specific parsing is kept away from business logic.

4. Swappable source interface

The pipeline can later use PRAW, another API, or non-Reddit sources.

5. Explicit reject reasons

Reject codes make tuning possible.

6. Semantic relevance instead of keyword-only filtering

Embedding anchors are a good lightweight classifier for broad technology
relevance.

7. Separate frustration and business relevance

This is important. A post can be technical but not painful, painful but not
commercial, or commercial but not emotionally frustrated.

8. Canonicalization before clustering

This is one of the best ideas in the repo. Stable business-facing wording makes
clustering much more meaningful.

9. Store validated intelligence, not raw scrape volume

This keeps the system focused on market intelligence rather than becoming a data
dump.

10. Cluster repeated pain themes

Clustering is what turns anecdotes into opportunity evidence.

## What To Improve Before Recreating

These should be fixed in a serious rebuild:

1. Make persistence architecture consistent

Choose database-backed or in-memory. Do not mix them. For production, use
database-backed runs, records, rejects, and opportunities.

2. Add migrations

The code defines database models but does not include usable Alembic migration
files. A professional system must be deployable from a clean database.

3. Add run-scoped data modeling

Canonical records need `run_id`, source id, and analysis window fields.

4. Fix transaction ownership

Repositories should not commit if the service/job owns the transaction.

5. Fix clustering for small datasets

UMAP/HDBSCAN parameters must adapt to record count, or clustering should be
skipped until enough records exist.

6. Implement true async jobs

Ingestion should be a background job, not one long HTTP request.

7. Version models, prompts, thresholds, and policies

Without versioning, results are hard to reproduce or compare.

8. Build evaluation datasets

Thresholds need labeled examples and measured precision/recall.

9. Add observability

Track per-stage latency, pass rates, reject rates, model errors, LLM costs, and
source failures.

10. Make business scoring explainable

Scores should include contributing factors, not just a number.

## Recommended Professional Architecture

A more robust version should look like this:

```text
API
  creates runs, reads status, reads intelligence

Job Queue
  schedules ingestion, canonicalization, embedding, clustering

Source Connectors
  Reddit public JSON, Reddit API/PRAW, future sources

Pipeline Worker
  metadata filter
  semantic tech relevance
  product/entity extraction
  frustration detector
  workflow/business detector
  business validation
  canonicalization
  intelligence record builder

Persistence
  ingestion_runs
  source_fetches
  candidate_posts or short-lived raw cache
  pipeline_rejects
  intelligence_records
  embeddings
  clusters
  cluster_memberships
  opportunities

Analytics Worker
  clustering
  aggregation
  trend detection
  scoring

Review UI
  accepted records
  rejected samples
  threshold tuning
  cluster review
```

## Suggested Database Model

Minimum production tables:

### ingestion_runs

- id
- status
- discovery_plan JSON
- policy_version
- started_at
- finished_at
- error_message
- counts by stage

### source_fetches

- id
- run_id
- source_type
- source_name
- query
- sort
- limit
- fetched_count
- failed_count
- error_message

### intelligence_records

- id
- run_id
- source_post_id
- source_type
- subreddit/source_name
- permalink
- title
- body or body_hash
- product/company fields
- canonical problem fields
- scores
- model versions
- policy version
- embedding id
- created_at

### pipeline_rejects

- id
- run_id
- source_post_id
- stage
- reason_code
- detail
- sampled_text or text_hash
- created_at

### embeddings

- id
- intelligence_record_id
- model_name
- model_version
- input_text
- vector
- created_at

### clusters

- id
- analysis_window
- model_version
- algorithm
- params JSON
- theme
- size
- coherence_score
- created_at

### cluster_memberships

- cluster_id
- intelligence_record_id
- distance
- confidence

### opportunities

- id
- cluster_id
- problem_statement
- business_score
- score_explanation JSON
- supporting_record_count
- affected_tools
- affected_companies
- personas
- trend_metrics
- created_at

## Recommended Rebuild Algorithm

Use this as the logical algorithm:

```text
create ingestion run
load discovery plan
for each source in discovery plan:
    fetch posts with pagination and backoff
    normalize each post
    skip exact duplicates
    optionally skip near duplicates
    for each post:
        run metadata filter
        if rejected: log reject and continue

        run semantic tech relevance
        if rejected: log reject and continue

        extract product/company/entities

        detect frustration/pain
        if rejected by pain policy: log reject and continue

        detect workflow/business relevance

        validate business relevance
        if rejected: log reject and continue

        canonicalize into stable business schema
        validate canonical output

        build intelligence record
        generate embedding
        persist record and embedding

complete ingestion run

if enough validated records exist:
    fetch records for chosen analysis window
    cluster embeddings
    compute cluster metadata
    aggregate clusters into opportunities
    persist opportunities with supporting evidence
else:
    mark analysis skipped due to insufficient data
```

## Operational Considerations

### Cost Control

Order the pipeline to control cost:

1. Metadata filters
2. Deduplication
3. Embedding similarity
4. Small classifiers
5. LLM canonicalization
6. Embedding persistence
7. Clustering

Never call an LLM before cheap filters have removed obvious noise.

### Latency

Separate online and offline work:

- Online API creates jobs and returns status.
- Workers do ingestion and ML.
- Clustering can run after ingestion completes or on a schedule.

### Reliability

Use retries and failure isolation:

- source-level retries
- LLM retries with schema validation
- database retry on transient errors
- checkpoint progress after each source or batch
- idempotent writes using external post id

### Observability

Track:

- posts fetched per source
- pass/reject rate per stage
- model inference latency
- LLM latency and cost
- canonicalization fallback rate
- embedding generation failures
- clustering skipped/crashed/noise-only rates
- duplicate rate
- opportunity score distribution

### Evaluation

Create labeled datasets:

- 200 obvious non-tech posts
- 200 tech but no pain posts
- 200 consumer complaints
- 200 business workflow pain posts
- 100 high-value opportunity examples
- 100 tricky false positive examples

Evaluate:

- tech relevance precision/recall
- pain detection precision/recall
- business relevance precision/recall
- canonicalization consistency
- cluster coherence
- opportunity ranking quality

### Human Review

Use human review where ambiguity is expensive:

- unknown product/company extraction
- borderline business relevance
- high-scoring opportunities
- cluster names
- hallucinated vendor associations
- new category discovery

The goal is not to manually review every post. The goal is to review the places
where a small correction improves future automation.

## Final Recommendation

The idea is strong:

- discover broad social/product pain signals
- filter with cheap-to-expensive stages
- normalize noisy complaints into canonical business problems
- embed and cluster repeated pains
- aggregate clusters into opportunity intelligence

The most important parts to preserve are canonicalization before clustering,
explicit stage-level decisions, business relevance separation, and validated-only
persistence.

The most important parts to improve are database/run modeling, transaction
ownership, job execution, small-dataset clustering behavior, model/prompt/policy
versioning, and evaluation.

If rebuilding this elsewhere, treat the current repository as a conceptual
prototype, not a production blueprint. Copy the pipeline logic and sequencing,
but redesign the persistence, orchestration, observability, and clustering
safety from the beginning.
