# Phase 2+ — Global discovery & simplified API

## API (2 endpoints only)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/ingestion` | Global Reddit discovery → pipeline |
| GET | `/api/v1/intelligence/{run_id}` | List records; `?export=true` for download |

## Discovery ingestion

Sources (public JSON):

- `/r/all/{sort}.json`
- `/r/popular/{sort}.json`
- `/search.json?q=...&type=link`

Posts are deduplicated by Reddit id across sources. The **pipeline** decides relevance — not the fetch layer.

## Pipeline order

1. metadata (cheap pre-filter)
2. semantic_classifier
3. product_extraction
4. sentiment
5. workflow_pain
6. business_validation

## Config

See `.env.example`: `DISCOVERY_FEEDS`, `DISCOVERY_SEARCH_QUERIES`.
