# Opportunity Intel: Analysis Pipeline Deep Dive

This document provides a highly detailed, step-by-step architectural breakdown of exactly what happens across the entire stack when a user clicks the **"Analyze"** button in the Opportunity Intel UI.

---

## 🌊 High-Level Execution Flow

When a company name (e.g., "Airbnb") is submitted, the system transitions from a user click into a fully orchestrated, parallelized intelligence gathering pipeline:

1. **Frontend Trigger**: React dispatches an asynchronous HTTP request to the backend.
2. **Endpoint Reception**: FastAPI validates the request and orchestrates the process.
3. **Parallel Discovery (Async)**: The system simultaneously kicks off two intelligence pipelines using `asyncio`:
   - **Career Pipeline**: Hunts for ATS platforms and extracts active job postings.
   - **Blog Pipeline**: Searches for and scrapes engineering blogs for technical context.
4. **Data Normalization & Filtering**: Raw data is cleaned, filtered by recency (30 days), tagged for urgency, and normalized into a unified schema.
5. **Prioritization**: The combined signals are aggressively ranked, and only the absolute **Top 10** highest-confidence signals survive.
6. **AI Inference**: An LLM analyzes the Top 10 signals to synthesize a final executive recommendation.
7. **Persistence**: The results are saved to a relational database (`SQLite`/`PostgreSQL`).
8. **UI Rendering**: The finalized intelligence package is hydrated back into the frontend dashboard.

---

## 🔍 Deep Dive: Phase-by-Phase Breakdown

### Phase 1: Frontend Interaction & Request Generation
* **Location**: `frontend/src/components/dashboard/AnalyzeForm.tsx` & `DashboardPage.tsx`
* **Technologies**: React, Axios, TailwindCSS, Lucide React (Icons).

When the user types "Airbnb" and clicks "Analyze":
1. **State Management**: React enters a loading state (`isLoading = true`), showing a spinner to the user.
2. **Network Request**: An Axios `POST` request is fired to the backend proxy:
   ```http
   POST http://localhost:5174/api/v1/analyze
   Content-Type: application/json
   Body: { "company_name": "Airbnb" }
   ```
   *(Note: Vite's `server.proxy` dynamically forwards this request from port `5174` to the FastAPI backend on port `8000`.)*

### Phase 2: Backend Orchestration & Concurrent Processing
* **Endpoint**: `@router.post("/analyze")` inside `backend/app/api/v1/endpoints/analyze.py`
* **Technologies**: FastAPI, Python `asyncio`, Pydantic (Request Validation).

1. **Validation**: Pydantic validates the incoming `AnalyzeCompanyRequest` payload.
2. **Concurrency Engine**: To ensure the analysis takes **<10 seconds**, the backend does not wait for the career page search to finish before starting the blog search. It leverages `asyncio.gather()`:
   ```python
   career_task = run_career_pipeline(company_name)
   blog_task = run_blog_pipeline(company_name)
   (career_signals, ats), (blog_signals, blog) = await asyncio.gather(career_task, blog_task)
   ```

### Phase 3A: The Career Intelligence Pipeline
* **Location**: `backend/app/services/career/`
* **Technologies**: `httpx` (Async HTTP), `Tavily` / `Serper` (Search APIs).

1. **ATS Discovery**: The `ats_discovery.py` module uses Google search operators (e.g., `site:boards.greenhouse.io Airbnb`) via Serper to locate the company's job board.
2. **Slug Extraction**: A Regex pattern extracts the company slug (e.g., `airbnb`).
3. **Data Ingestion**: The system queries the public JSON APIs for platforms like **Greenhouse** or **Lever**.
4. **Signal Extraction & Normalization**:
   - Parses the raw JSON response.
   - Extracts metadata like `location`, `department`, and `timestamp` (`updated_at` or `createdAt`).
   - Tags the signal with an `urgency: "High"` rating if keywords like "immediate", "urgent", or "ASAP" are found.
   - Normalizes the output into a strictly typed `UnifiedSignalSchema`.

### Phase 3B: The Engineering Blog Pipeline
* **Location**: `backend/app/services/blog/`
* **Technologies**: `Firecrawl` (LLM-native Scraping).

1. **Blog Discovery**: Similar to the ATS, the system hunts for `{Company} engineering blog`.
2. **Markdown Scraping**: It utilizes the **Firecrawl API** to bypass modern web protections, render dynamic React/Next.js blog sites, and cleanly extract the content as raw Markdown.
3. **Keyword Mapping**: The text is scanned against a predefined `BLOG_PAIN_TAXONOMY` (found in `normalization.py`) to map technical phrases (like "monolith", "Kubernetes", "latency") to actionable business pain points (e.g., "Legacy Modernization", "Infrastructure Scaling").

### Phase 4: Filtering & Aggressive Prioritization
* **Location**: `pipeline.py` & `analyze.py`

To ensure high signal-to-noise ratio:
1. **Recency Filter**: The pipeline parses the `timestamp` using Python's `datetime`. Any job or blog older than **30 days** is completely dropped.
2. **Confidence Sorting**: The remaining combined signals (Career + Blog) are merged into one array. They are then sorted by their dynamically calculated `confidence` score in descending order.
3. **Hard Cap**: The system slices the array to keep only the **Top 10** absolute best signals:
   ```python
   all_signals.sort(key=lambda x: x.confidence, reverse=True)
   all_signals = all_signals[:10]
   ```

### Phase 5: AI Inference & Synthesis
* **Location**: `backend/app/services/ai/inference.py`
* **Technologies**: OpenRouter API, DeepSeek / Llama3, OpenAI SDK (for structured outputs).

1. **Prompt Construction**: The Top 10 filtered signals are converted into a compressed JSON string and injected into a strict system prompt.
2. **LLM Execution**: The AI (configured via `OPENROUTER_API_KEY`) is tasked with analyzing the holistic picture painted by these 10 signals. 
3. **Structured Output**: The LLM guarantees a valid JSON response matching the `AIOpportunityOutput` schema, containing:
   - A detected meta-opportunity.
   - 3 bullet points of deep reasoning.
   - Recommended outreach strategy (e.g., "Target the VP of Engineering with this specific angle").

### Phase 6: Database Persistence & Serialization
* **Location**: `backend/app/services/company_service.py` & `backend/app/models/signal.py`
* **Technologies**: SQLAlchemy (ORM), SQLite (Development Data Store).

1. **Transaction Setup**: A SQLAlchemy `Session` is initiated.
2. **Data Mapping**: The Pydantic `UnifiedSignalSchema` instances are mapped to the SQLAlchemy `Signal` ORM models.
   - *Technical Note*: The string `timestamp` is converted back to a Python `datetime` object here to satisfy SQLite's strict typing (`datetime.fromisoformat()`).
3. **Commit**: The top 10 records are flushed and committed to the `dev.db` database, safely associating them with the company's `uuid`.
4. **Serialization**: The ORM objects (which now possess database-generated `uuid` keys) are dumped back into JSON using `SignalResponse.model_dump()`.

### Phase 7: UI Hydration
1. **Response Returned**: FastAPI sends the serialized JSON back to the Axios client with an HTTP 200 status.
2. **DOM Update**: React receives the payload, triggering a state update (`setAnalyzeResult`).
3. **Render**: The `AnalysisResult.tsx` component iterates over the Top 10 signals, rendering highly interactive `SignalCard` components.
   - The UI intelligently calculates relative time (e.g., "5 days ago") from the timestamps.
   - Renders red "URGENT" tags.
   - Allows deep-dive modal inspections (`SignalDetail.tsx`) via React state.

---

## 🛠️ Complete Tech Stack Summary

### **Frontend Architecture**
- **Framework**: `React 18` (via `Vite` for HMR and lightning-fast builds).
- **Styling**: `TailwindCSS` with custom brand tokens and glassmorphic UI elements.
- **Icons**: `Lucide React` for lightweight, scalable SVG iconography.
- **Routing**: `React Router DOM` for SPA navigation.
- **Network**: `Axios` for robust API communication.

### **Backend Architecture**
- **Framework**: `FastAPI` (Python 3.10+) for high-performance, asynchronous endpoints.
- **Validation**: `Pydantic v2` for strict typing, schema enforcement, and JSON serialization.
- **Database**: `SQLite` (via `SQLAlchemy` ORM) for persistent local storage, easily scalable to PostgreSQL via Neon DB in production.
- **Concurrency**: Native `async/await` and `asyncio.gather` for parallel network bound tasks.

### **External Intelligence APIs**
- **Search**: `Tavily` or `Serper (Google Search API)` for programmatic discovery.
- **Extraction**: `Firecrawl` for LLM-native web scraping and Markdown conversion.
- **LLM/Inference**: `OpenRouter` serving state-of-the-art models for synthesizing the intelligence.
