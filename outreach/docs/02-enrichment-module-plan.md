# Technical Design Document: Opportunity Enrichment & Decision Maker Discovery

**Module:** Phase 4 - Contact Enrichment & UI Integration
**Objective:** Automate the discovery of key decision-makers for companies exhibiting technical pain points, bridging the gap between raw data signals and direct sales action.

---

## 1. System Architecture & Component Additions
This phase extends our existing FastAPI pipeline by integrating a third-party B2B data provider (Apollo.io) and updating the Pydantic schemas to support contact data.

* **Data Provider:** Apollo.io REST API (`/v1/mixed_people/search`)
* **HTTP Client:** `httpx` (Asynchronous execution to prevent blocking)
* **Authentication:** Master API Key loaded securely via `.env`
* **Data Validation:** Pydantic (New `DecisionMaker` and `EnrichedOpportunity` schemas)

---

## 2. Dynamic Persona Mapping (The Strategy)
Before querying Apollo, the system must determine *who* to contact based on the extracted technical signal.

* **Cloud Migration / DevOps Signals:** Target `["VP of Engineering", "Head of Infrastructure", "Chief Technology Officer"]`
* **Data / Backend Bottlenecks:** Target `["VP of Data", "Director of Engineering", "Head of Backend"]`
* **AI / ML Expansion:** Target `["Chief Data Officer", "VP of Artificial Intelligence", "CTO"]`

*Implementation Note:* For the hackathon MVP, a static mapping dictionary or a lightweight LLM router will translate the `opportunity_category` into a list of target titles.

---

## 3. Backend Implementation: `enrichment.py`
To strictly maintain modularity, all Apollo API logic must reside in a dedicated file.

### Step 1: Pydantic Schema Updates (`schemas.py`)
```python
class DecisionMaker(BaseModel):
    name: str
    exact_title: str
    linkedin_url: Optional[str]
    email: Optional[str]
    confidence_score: Optional[int]

class EnrichedOpportunity(ProcessedJobSignal):
    company_domain: str
    decision_makers: List[DecisionMaker]