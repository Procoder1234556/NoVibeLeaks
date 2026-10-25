"""Multi-parameter security score (0–100, higher is better)."""

from __future__ import annotations

from typing import Any

_SEVERITY_PENALTY = {
    "critical": 25,
    "high": 12,
    "medium": 6,
    "low": 3,
}

_CATEGORY_KEYS = ("secrets", "api_keys", "configuration", "code_quality")


def score_from_findings(
    secret_findings: list[dict[str, Any]],
    vibe_findings: list[dict[str, Any]],
    api_key_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    api_key_results = api_key_results or []

    buckets: dict[str, list[dict[str, Any]]] = {k: [] for k in _CATEGORY_KEYS}
    for f in secret_findings:
        buckets["secrets"].append(f)
    for f in vibe_findings:
        cat = str(f.get("category", "code_quality")).lower()
        if cat == "configuration":
            buckets["configuration"].append(f)
        else:
            buckets["code_quality"].append(f)

    for r in api_key_results:
        st = r.get("status")
        if st == "invalid":
            buckets["api_keys"].append(
                {
                    "severity": "critical",
                    "message": r.get("message", "Invalid API key"),
                    "rule": f"api_key_{r.get('provider', 'unknown')}",
                }
            )
        elif st == "rate_limited":
            buckets["api_keys"].append(
                {
                    "severity": "low",
                    "message": r.get("message", "Rate limited during key check"),
                    "rule": "api_key_rate_limited",
                }
            )

    breakdown: dict[str, Any] = {}
    scores: list[float] = []
    for key in _CATEGORY_KEYS:
        penalty = sum(_SEVERITY_PENALTY.get(str(f.get("severity", "medium")).lower(), 6) for f in buckets[key])
        sub = max(0.0, 100.0 - penalty)
        breakdown[key] = {
            "score": round(sub, 1),
            "finding_count": len(buckets[key]),
            "findings": buckets[key][:20],
        }
        scores.append(sub)

    overall = round(sum(scores) / len(scores), 1) if scores else 100.0
    grade = _grade(overall)
    return {
        "overall_score": overall,
        "grade": grade,
        "breakdown": breakdown,
        "summary": _summary(overall, secret_findings, vibe_findings, api_key_results),
    }


def _grade(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _summary(
    overall: float,
    secrets: list[dict[str, Any]],
    vibe: list[dict[str, Any]],
    api_results: list[dict[str, Any]],
) -> str:
    parts = [f"Overall security score: {overall}/100."]
    if secrets:
        parts.append(f"{len(secrets)} secret pattern(s) detected — rotate and remove from source.")
    if vibe:
        parts.append(f"{len(vibe)} code/configuration issue(s) found.")
    invalid = [r for r in api_results if r.get("status") == "invalid"]
    if invalid:
        parts.append(f"{len(invalid)} API key(s) failed validation.")
    if not secrets and not vibe and not invalid:
        parts.append("No high-confidence issues in this scan.")
    return " ".join(parts)
