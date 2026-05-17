# Frontend plan (Vite + React)

## Bootstrap

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install @tanstack/react-query react-router-dom
# optional: axios or native fetch wrapper
```

Dev proxy in `vite.config.ts`:

```ts
server: {
  proxy: {
    '/api': 'http://localhost:8000',
  },
},
```

## App goals

Support operators who need to **configure**, **run**, and **explore** extracted Reddit intelligence—not run NLP in the browser.

## Routes

| Path | Screen | Purpose |
|------|--------|---------|
| `/` | Dashboard | Recent runs, counts, quick stats |
| `/runs` | Ingestion runs | List/history, trigger new run |
| `/runs/:id` | Run detail | Progress, rejected breakdown by stage |
| `/intelligence` | Explorer | Table/cards of validated records |
| `/intelligence/:id` | Detail | Full JSON payload viewer |
| `/settings/subreddits` | Targets | Enable/disable subreddits, limits |
| `/settings/pipeline` | Thresholds | min length, upvotes, recency, keywords |
| `/settings/products` | Known products | CRUD mapping |

## Key UI components

```text
src/
├── api/client.ts           # fetch wrapper, base URL
├── api/hooks/              # react-query hooks per resource
├── components/
│   ├── Layout.tsx
│   ├── RunStatusBadge.tsx
│   ├── IntelligenceTable.tsx
│   ├── JsonViewer.tsx
│   └── ConfigForm.tsx
└── pages/                  # route pages
```

## API integration (react-query)

| Hook | Endpoint |
|------|----------|
| `useIngestionRuns()` | `GET /api/v1/ingestion/runs` |
| `useStartRun()` | `POST /api/v1/ingestion/runs` |
| `useIntelligence(filters)` | `GET /api/v1/intelligence` |
| `usePipelineConfig()` | `GET/PATCH /api/v1/config/pipeline` |
| `useSubreddits()` | `GET/PUT /api/v1/config/subreddits` |

Polling: while run `status === "running"`, refetch run detail every 3–5s.

## Intelligence explorer UX

**Table columns (MVP):**

- Subreddit, title (truncated), product, company
- Sentiment (color-coded), workflow pain badge
- Upvotes, date, link to Reddit (`permalink` from payload)

**Filters panel:**

- Subreddit multi-select
- Product/company text
- Sentiment range slider
- Toggle: workflow pain only
- Date range

**Export button:** calls `GET /api/v1/intelligence/export` with current filters; download `intelligence-YYYY-MM-DD.json`.

## Dashboard widgets (MVP)

- Total intelligence records
- Records last 7 days
- Top products by count (aggregate client-side or future `GET /analytics/summary`)
- Last run status

## Styling

- Keep minimal and readable: system font or one sans stack.
- No design system requirement for MVP; consistent spacing (8px grid) and accessible contrast.

## Type safety

Generate types from FastAPI OpenAPI:

```bash
npx openapi-typescript http://localhost:8000/openapi.json -o src/api/schema.d.ts
```

Map `IntelligenceRecordOut` to table row type.

## Environment

```bash
# frontend/.env.development
VITE_API_BASE_URL=/api/v1
```

Production: full API URL to deployed FastAPI.

## Out of scope (frontend)

- Reddit OAuth in browser
- Local ML inference
- Real-time WebSockets (polling sufficient for MVP)
