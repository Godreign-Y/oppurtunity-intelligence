# Phase 1 implementation notes

## Ingestion swap design

```
services/IngestionService
        │
        ▼
ingestion/factory.create_reddit_source()
        │
   ┌────┴────┐
   ▼         ▼
public_json  praw (stub)
   │
   ▼
RedditSource.iter_subreddit_posts() → RawRedditPost
        │
        ▼
pipelines/PipelineOrchestrator (one post at a time)
        │
        ▼
filters/* (ordered registry)
```

`RawRedditPost` is the only type crossing the ingestion boundary.

## Public JSON endpoints

- `GET https://www.reddit.com/r/{subreddit}/{sort}.json?limit=N`
- Requires `User-Agent` header (`REDDIT_USER_AGENT`)
- Phase 1: single page per subreddit; delay between subreddits via `REDDIT_REQUEST_DELAY_SECONDS`

## Filter stages (Phase 1)

| Stage | Status |
|-------|--------|
| metadata | Implemented |
| tech_keywords | Implemented |
| semantic_classifier | Placeholder (pass) |
| product_extraction | Placeholder |
| business_validation | Placeholder |
| sentiment | Placeholder |
| workflow_pain | Placeholder |
| embeddings | Placeholder |
| clustering | Placeholder (batch-oriented) |

## Storage

- Phase 1: `InMemoryRunStore` — run summaries + passed post results only
- Phase 2+: Neon + Alembic; intelligence JSON at Step 10

## API routes

| Method | Path |
|--------|------|
| GET | `/api/v1/health` |
| GET | `/api/v1/health/config` |
| POST | `/api/v1/ingestion/runs` |
| POST | `/api/v1/ingestion/runs/quick` |
| GET | `/api/v1/ingestion/runs` |
| GET | `/api/v1/ingestion/runs/{run_id}` |
| GET | `/api/v1/ingestion/runs/{run_id}/passed` |
