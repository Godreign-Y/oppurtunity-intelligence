"""
Signal normalization rules.
"""


def classify_signal(text: str) -> str:
    text = text.lower()

    if any(k in text for k in [
        "deployment failed",
        "deployment failure",
        "deployment failed for",
        "deployment workflow failed",
        "rollback",
        "deploy failed"
    ]):
        return "DEPLOYMENT_INSTABILITY"

    if any(k in text for k in ["latency", "slow"]):
        return "PERFORMANCE_DEGRADATION"

    if any(k in text for k in ["outage", "downtime"]):
        return "SERVICE_OUTAGE"

    if "error" in text:
        return "GENERAL_FAILURE"

    return "UNKNOWN"

def detect_ecosystem(text: str) -> str:
    text = text.lower()

    if any(k in text for k in ["kubernetes", "aks", "cluster", "pod", "helm"]):
        return "cloud"

    if any(k in text for k in ["gpu", "cuda", "inference"]):
        return "ai-infra"

    return "general"

def detect_severity(text: str) -> str:
    text = text.lower()

    if "failed" in text or "outage" in text:
        return "high"

    if "slow" in text or "latency" in text:
        return "medium"

    return "low"

def calculate_confidence(text: str) -> float:
    score = 0.5

    if "failed" in text:
        score += 0.2
    if "error" in text:
        score += 0.1
    if "urgent" in text:
        score += 0.2

    return min(score, 1.0)
