# Technical Design Document: Hiring Intelligence Data Pipeline

**Module:** Opportunity Detection via Job Market Signals
**Objective:** Continuously extract, process, and structure hiring data from product-based companies to identify technical pain points and generate actionable sales intelligence.

---

## 1. System Architecture & Tech Stack
To ensure speed, stability, and zero friction during the hackathon, this module will be built strictly on the team's standardized architecture.

* **Backend Framework:** FastAPI (Python 3.11.x)
* **Package Manager:** `uv` (Strictly enforced for hyper-fast dependency resolution)
* **Database:** Neon (Serverless PostgreSQL)
* **Migrations:** Alembic
* **Data Validation:** Pydantic
* **HTTP Client:** `httpx` (for asynchronous API calls)

---

## 2. Data Acquisition Strategy (The Extract)
To avoid bot-mitigation roadblocks (CAPTCHAs, IP bans) common with direct web scraping, we will utilize aggregator APIs to fetch structured job postings globally.

* **Primary Source:** SerpApi (Google Jobs API endpoint)
* **Secondary Fallback:** Adzuna API
* **Target Filters:**
  * `company_type`: Product-based tech companies.
  * `role_keywords`: "DevOps", "Cloud Migration", "AI Engineer", "Site Reliability", "Security Architect".
* **Execution:** A scheduled async function in FastAPI will hit the endpoint, fetching paginated JSON results containing the job title, company name, posting date, and full job description.

---

## 3. Data Processing & Transformation (The Transform)
Raw job descriptions contain heavy noise (e.g., "Equal Opportunity Employer" statements, generic perks). The processing layer will clean and standardize this text.

* **Validation:** All incoming API responses will immediately pass through a Pydantic model (`RawJobPosting`) to enforce type strictness.
* **Sanitization:** * Strip all raw HTML tags using basic regex or BeautifulSoup.
  * Remove non-essential boilerplate text.
* **Signal Extraction (Keyword Matching):**
  * Implement a lightweight, modular tagging function to scan the sanitized description for tech-stack keywords (e.g., AWS, GCP, Kubernetes, Legacy, Migration).
  * These extracted tags form the crucial context that the Explainability Engine will use to map the problem to our IT service solutions.

---

## 4. Relational Database Schema (The Load)
Using Neon and Alembic, we will establish a clean, relational structure to store the processed signals.

### `companies` Table
* `id` (UUID, Primary Key)
* `name` (String, Unique)
* `domain` (String)

### `job_signals` Table
* `id` (UUID, Primary Key)
* `company_id` (UUID, Foreign Key)
* `job_title` (String)
* `sanitized_description` (Text)
* `posted_date` (Date)

### `extracted_insights` Table
* `id` (UUID, Primary Key)
* `job_id` (UUID, Foreign Key)
* `detected_tech_stack` (Array of Strings)
* `opportunity_category` (String) (e.g., "Cloud Migration", "AI Integration")

---

## 5. Development Workflow & Strict Guidelines
To ensure parallel development without merge conflicts or technical debt, all work on this module will adhere to the following rules:

1. **Package Management:** Use `uv` exclusively. No exceptions for `pip` or `poetry`.
2. **Database Management:** Execute database schema changes using Alembic *only*. Do not run raw SQL DDL commands against the Neon database.
3. **Modularity:** Separate the extraction (`fetcher.py`), transformation (`processor.py`), and storage (`db_loader.py`) logic into independent modules.
4. **Typing & Documentation:** Apply Python type hints to all variables, functions, and class methods. Write concise Google-style docstrings for every function.
5. **Implementation:** Mocking is strictly prohibited. If an API key fails or a real implementation is blocked, development must pause to explain and resolve the blocker rather than writing a mock function.

---

## 6. Version Control Protocol
Clean Git practices are mandatory for hackathon speed.

* **Branching:** Ensure all code for this pipeline is committed and pushed directly to the `v1` branch. Do not use or push to a `v0` branch, as this introduces severe versioning errors and deployment conflicts for the frontend team.
* **Commits:** Commit early and often, ideally after completing each of the three pipeline phases (Extract, Transform, Load).
* **Locking:** Once the module successfully writes a verified JSON output to the database, the logic will be considered a "lock." Further modifications will only be made if the AI Explainability Engine requires different formatting.