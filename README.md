# REDIT — Reddit Opportunity Intelligence Engine

## Overview

REDIT is an AI-powered backend system that discovers workflow pains, developer frustrations, operational bottlenecks, and recurring business problems from Reddit discussions.

The system ingests Reddit posts, filters meaningful workflow pain using semantic AI pipelines, canonicalizes noisy discussions into structured intelligence, generates embeddings, clusters semantically similar pain points, and stores business intelligence for downstream analytics and retrieval.

---

# Core Idea

Most Reddit discussions are noisy, emotional, repetitive, or irrelevant.

REDIT transforms unstructured Reddit discussions into:

* normalized workflow pain statements
* structured business intelligence
* semantic embeddings
* clustered operational pain themes
* searchable business insights

The goal is to surface:

* infrastructure pain
* DevOps bottlenecks
* developer workflow frustrations
* AI tooling pain points
* operational inefficiencies
* emerging business opportunities

---

# High-Level Architecture

```text
                ┌───────────────────┐
                │    Reddit APIs    │
                └─────────┬─────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │ Discovery Pipeline  │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Semantic Filtering  │
              │ Workflow Detection  │
              │ Frustration Scoring │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Canonicalization    │
              │ Intelligence Build  │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Embedding Generation│
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ PostgreSQL +        │
              │ pgvector Storage    │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ UMAP + HDBSCAN      │
              │ Semantic Clustering │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Aggregated Business │
              │ Intelligence        │
              └─────────────────────┘
```

---

# Pipeline Stages

## Stage 1 — Discovery + Semantic Filtering

The ingestion system fetches Reddit posts from:

* subreddits
* global feeds
* Reddit search

Each post passes through multiple semantic filters.

### Filters Include

* workflow pain detection
* frustration scoring
* business relevance detection
* metadata validation
* semantic classification

Only high-signal posts continue through the pipeline.

---

## Stage 2 — Canonicalization + Intelligence Extraction

Accepted posts are transformed into structured intelligence objects.

The system extracts:

* normalized problem statement
* pain category
* business impact
* frustration score
* business relevance
* affected tools
* affected platforms
* potential companies affected

This removes Reddit noise and converts discussions into clean intelligence records.

---

## Stage 3 — Embedding Generation + Persistence

Validated intelligence records are embedded using SentenceTransformers.

The embeddings are stored inside PostgreSQL using `pgvector`.

This enables:

* semantic search
* similarity retrieval
* clustering
* future recommendation systems
* opportunity mining

---

## Stage 4 — Semantic Clustering (Experimental)

Stored embeddings are fetched and grouped using:

* UMAP for dimensionality reduction
* HDBSCAN for density-based clustering

The clustering layer attempts to identify:

* recurring workflow pains
* repeated operational bottlenecks
* emerging tooling frustrations
* semantically related business problems

### Current Clustering Flow

```text
Embeddings
↓
UMAP dimensionality reduction
↓
HDBSCAN clustering
↓
In-memory cluster analysis
↓
Business intelligence aggregation
```

### Notes

* clustering currently runs in-memory
* intermediate cluster tables are not persisted
* aggregation only runs if valid clusters are detected
* clustering quality improves with larger datasets

---

# Tech Stack

| Layer           | Technology           |
| --------------- | -------------------- |
| Backend API     | FastAPI              |
| Async Runtime   | asyncio              |
| Package Manager | uv                   |
| Database        | PostgreSQL           |
| Vector Storage  | pgvector             |
| ORM             | SQLAlchemy Async     |
| ML Embeddings   | SentenceTransformers |
| Clustering      | UMAP + HDBSCAN       |
| LLM Extraction  | Groq API             |
| HTTP Client     | httpx                |

---

# Why `uv`?

This project uses `uv` instead of pip because:

* extremely fast dependency resolution
* reproducible environments
* modern Python workflow
* better virtual environment handling

---

# Project Structure

```text
backend/src/redit/

├── aggregation/          # Business intelligence aggregation
├── api/                  # FastAPI endpoints
├── canonicalization/     # LLM-based normalization
├── clustering/           # UMAP + HDBSCAN semantic clustering
├── config/               # Settings & environment config
├── embeddings/           # Embedding generation
├── filters/              # Semantic filter stages
├── ingestion/            # Reddit ingestion sources
├── intelligence/         # Intelligence builders
├── ml/                   # ML models and scoring
├── pipelines/            # Pipeline orchestration
├── services/             # High-level services
├── storage/              # Database models/repositories
└── utils/                # Logging and utilities
```

---

# Database Tables

## `canonical_intelligence`

Stores validated and embedded intelligence records.

### Contains

* normalized workflow pain
* metadata
* semantic embeddings
* business scoring

---

## `final_business_intelligence`

Stores aggregated business intelligence generated from semantic clusters.

### Contains

* cluster themes
* representative problem statements
* supporting post counts
* business scores
* aggregated frustration signals

---

# Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key

DATABASE_URL=postgresql://username:password@host/dbname?ssl=require
```

---

# Installation

## 1. Clone Repository

```bash
git clone <repo_url>
cd REDIT
```

---

## 2. Install uv

```bash
pip install uv
```

---

## 3. Create Virtual Environment

```bash
uv venv
```

---

## 4. Activate Environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / Mac

```bash
source .venv/bin/activate
```

---

## 5. Install Dependencies

```bash
uv sync
```

---

# Running the Backend

From project root:

```bash
cd backend/src
```

Run FastAPI server:

```bash
uv run uvicorn redit.main:app --reload --host 0.0.0.0 --port 8000
```

---

# Swagger Docs

After startup:

```text
http://localhost:8000/docs
```

---

# Example Ingestion Payload

```json
{
  "source_mode": "hybrid",
  "subreddits": [
    "devops",
    "kubernetes",
    "terraform",
    "sysadmin",
    "sre",
    "backend",
    "MLOps"
  ],
  "limit_per_source": 15,
  "sort": "new",
  "dry_run": false
}
```

---

# Example End-to-End Flow

```text
1. Reddit posts fetched
2. Semantic filtering executed
3. Workflow pain detected
4. Post canonicalized
5. Intelligence object created
6. Embedding generated
7. Stored in PostgreSQL
8. Embeddings clustered
9. Aggregated business intelligence generated
```

---

# Current Status

## Stable Features

* staged ingestion pipeline
* semantic filtering
* canonical intelligence extraction
* async-safe embedding generation
* PostgreSQL + pgvector persistence
* NeonDB compatibility

## Experimental Features

* semantic clustering
* UMAP/HDBSCAN aggregation
* recurring pain discovery

---

# Future Improvements

* vector search API
* semantic retrieval dashboard
* real-time ingestion workers
* Redis/Kafka queue architecture
* batched transformer inference
* GPU acceleration
* opportunity trend analytics
* company pain heatmaps

---

# Key Design Principles

* semantic-first filtering
* async-safe architecture
* staged ingestion pipelines
* modular filter system
* vector-native storage
* production-oriented transaction handling

---

# License

MIT License
