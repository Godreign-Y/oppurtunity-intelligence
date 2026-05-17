# Enrichment Module (Phase 4)

## Feature Overview

The Enrichment Module bridges the critical gap between raw technical job signals and actionable sales intelligence. By taking a processed job posting (including its extracted tech stack and company name), this module programmatically discovers key decision-makers at the target company. This transforms a simple job lead into a highly enriched, ready-to-action opportunity for the sales and outreach teams.

## Tech Stack & Integrations

- **Async Networking:** Utilizes `httpx` and `asyncio` for high-performance, non-blocking asynchronous HTTP requests.
- **Data Validation:** Employs **Pydantic** for strict schema validation, ensuring that all data flowing into the frontend or database adheres to defined types and structures.
- **Data Provider:** Integrates with the **Hunter.io Domain Search API** (`/v2/domain-search`) to discover validated contacts within specific departments.
- **Graceful Degradation:** The module is built with resilient `try/except` error handling. If the Hunter API fails (e.g., rate limits, invalid parameters, or network issues), the pipeline logs the error and gracefully returns an empty list `[]` of decision-makers, preventing the entire application pipeline from crashing.

## The Data Flow

The enrichment process follows a strictly typed, sequential data flow:

1. **Domain Extraction:** The raw company name (e.g., "Boeing") is parsed and cleaned to extract a simplified company domain (e.g., `boeing.com`).
2. **Department Mapping:** The job's detected tech stack drives the targeted outreach. The module maps these technical requirements to the appropriate Hunter.io department filters (e.g., targeting the `it` department for engineering and IT infrastructure roles).
3. **API Invocation:** An asynchronous `GET` request is made to the Hunter API, passing the domain and target department.
4. **Schema Validation:** The JSON response is parsed, and the returned emails and contact details are mapped directly into strict Pydantic `DecisionMaker` models.

## Pydantic Schemas

To ensure strict data contracts across the application, the module relies on two primary schemas:

- **`DecisionMaker`**: Represents an individual contact discovered at the target company.
  - `first_name` (Optional[str])
  - `last_name` (Optional[str])
  - `title` (Optional[str])
  - `email` (Optional[str])

- **`EnrichedOpportunity`**: Inherits from `ProcessedJobSignal` and aggregates the original job data with the newly discovered intelligence.
  - Inherits: `job_title`, `company_name`, `posted_date`, `sanitized_description`, `detected_tech_stack`
  - Adds: `company_domain` (str)
  - Adds: `decision_makers` (List[DecisionMaker])

## Example JSON Output

Below is a sample JSON payload demonstrating a fully enriched opportunity, ready for frontend consumption:

```json
{
  "job_title": "Mid-Level DevOps Developer",
  "company_name": "Boeing",
  "posted_date": "3 days ago",
  "sanitized_description": "Hazelwood, Missouri; Salt Lake City, Utah; Huntsville, Alabama...",
  "detected_tech_stack": [
    "AWS",
    "GCP",
    "Azure",
    "Kubernetes",
    "Python",
    "Node.js",
    "Migration",
    "CI/CD"
  ],
  "company_domain": "boeing.com",
  "decision_makers": [
    {
      "first_name": "Jessica",
      "last_name": "Carlton",
      "title": "Lead In Technology",
      "email": "jessica.m.carlton@boeing.com"
    },
    {
      "first_name": "David",
      "last_name": "Nelson",
      "title": "Senior Software Engineer",
      "email": "david.nelson@boeing.com"
    }
  ]
}
```

## Local Setup

> **Note:** To run this module locally, you must ensure that your `HUNTER_API_KEY` is set in your `.env` file.
