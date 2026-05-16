

***

#  Technical Signal Intelligence Platform (MVP)

***

##  Overview

This project builds a backend system that transforms:

```
Raw GitHub engineering issues
→ Structured operational intelligence
```

It detects:

* deployment failures
* performance problems
* outages
* and aggregates them to identify patterns and affected organizations

***

#  Core Idea (Intuitive)

```
Ingestion   = What happened  
Normalization = What it means  
Insights    = What matters  
```

***

#  System Pipeline

```
GitHub API
    ↓
github_signals (raw structured data)
    ↓
normalized_signals (interpreted signals)
    ↓
insights (aggregated intelligence)
```

***

#  Step-by-Step (Intuitive Explanation)

***

## 🔹 1. Ingestion (Data Collection)

**File:**

```
app/services/github/service.py
```

### What it does:

* Fetches GitHub issues
* Extracts relevant fields (title, content, metadata)
* Stores them in the database

### Intuition:

>  “Collect everything happening in the real world”

Example:

```
"Helm deployment failed due to timeout"
```

→ stored as **raw data**

***

##  2. Storage Layer

**Files:**

```
app/models/github_signal.py
app/repositories/github_signal_repository.py
```

### What it does:

* Stores structured signals in `github_signals` table
* Prevents duplicates using `external_id`

### Intuition:

>  “Keep everything organized so it can be processed later”

***

## 🔹 3. Normalization (Most Important Step)

**File:**

```
app/services/normalization/service.py
```

### What it does:

* Combines:
  ```
  title + content
  ```
* Scans text for keywords
* Converts raw text → structured signal

***

## 🔹 How normalization works (core logic)

### Keywords → Signal Types

Example:

```
Text:
"Helm deployment failed due to timeout"
```

Detected:

| Keyword           | Meaning                  |
| ----------------- | ------------------------ |
| deployment failed | DEPLOYMENT\_INSTABILITY  |
| timeout           | PERFORMANCE\_DEGRADATION |
| helm              | cloud ecosystem          |

***

### Final output:

```json
{
  "signal_type": "DEPLOYMENT_INSTABILITY",
  "ecosystem": "cloud",
  "severity": "high"
}
```

***

### Intuition:

>  “Translate messy text into structured meaning”

***

## 🔹 4. Keyword Detection Logic

**Location (your project):**

```
app/services/normalization/service.py
OR inside rules logic
```

***

### Pattern used:

```python
if any(k in text for k in [
    "deployment failed",
    "rollback",
    "helm error"
]):
    signal = "DEPLOYMENT_INSTABILITY"
```

***

### Important concept:

```
Many keywords → One signal 
```

***

### Why?

Users write differently:

```
deploy failed  
release failed  
rollback error  
pipeline crash  
```

But all mean:

```
DEPLOYMENT_INSTABILITY 
```

***

## 🔹 5. Insights (Aggregation Layer)

**File:**

```
app/services/insights/service.py
```

***

### What it does:

Runs queries like:

```sql
SELECT signal_type, COUNT(*)
FROM normalized_signals
GROUP BY signal_type;
```

***

##  What insights you generate:

***

###  Top Problems

```
DEPLOYMENT_INSTABILITY dominates
```

***

###  Affected Organizations

```
FreeForCharity → 9 issues
shredstack → 6 issues
```

***

###  Severity Distribution

```
high → many issues
```

***

### Intuition:

>  “Find patterns across all collected signals”

***

#  What Your System Evaluates

***

| Factor       | Meaning              |
| ------------ | -------------------- |
| signal\_type | What kind of problem |
| ecosystem    | where it's happening |
| severity     | how serious          |
| organization | who is affected      |
| frequency    | how often            |

***

#  How To Run

***

##  1. Run migrations

```bash
alembic upgrade head
```

***

##  2. Ingest GitHub data

```bash
python -m app.test_github
```

***

##  3. Normalize signals

```bash
python -m app.test_normalization
```

***

##  4. Generate insights

```bash
python -m app.test_insights
```

***

#  Example Output

***

### Top Signal Types

```
DEPLOYMENT_INSTABILITY → highest
```

***

### Top Organizations

```
FreeForCharity
shredstack
sombaner
```

***

### Insight

```
Deployment failures dominate across multiple repositories,
especially in cloud environments.
```

***

#  Why Normalization is Necessary

***

## Without normalization

```
"deployment failed"
"deploy failed"
"rollback error"
```

→ seen as separate 

***

## With normalization

```
ALL → DEPLOYMENT_INSTABILITY 
```

***

→ enables:

 pattern detection  
 aggregation  
 insights

***

#  Key Files (What Matters)

***

## Ingestion

```
app/services/github/service.py
```

***

## Storage

```
app/models/github_signal.py
app/repositories/github_signal_repository.py
```

***

## Normalization

```
app/services/normalization/service.py
```

***

## Insights

```
app/services/insights/service.py
```

***

#  Current Limitations

* Rule-based keyword detection
* Limited keyword coverage
* Ecosystem classification is basic

***

#  Next Improvements

* Add more keywords
* Improve ecosystem detection
* Add trend tracking
* Add scoring for organizations

