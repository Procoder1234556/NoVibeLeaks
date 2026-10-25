"""Sanitize scanner output for Phase 3 web API and Supabase storage."""

from __future__ import annotations

from typing import Any

_MAX_CODE_BYTES = 2 * 1024 * 1024


def _location(finding: dict[str, Any]) -> dict[str, Any]:
    loc = finding.get("location")
    if isinstance(loc, dict):
        return {
            "file": loc.get("file") or finding.get("file") or "<unknown>",
            "line": int(loc.get("line") or finding.get("line") or 0),
            "column": int(loc.get("column") or finding.get("column") or 0),
        }
    return {
        "file": str(finding.get("file") or "<unknown>"),
        "line": int(finding.get("line") or 0),
        "column": int(finding.get("column") or 0),
    }


def sanitize_finding(finding: dict[str, Any]) -> dict[str, Any]:
    """Rule + location only — never echo matched secret material."""
    return {
        "rule": finding.get("rule"),
        "severity": finding.get("severity"),
        "category": finding.get("category"),
        "message": finding.get("message"),
        "recommendation": finding.get("recommendation"),
        "location": _location(finding),
    }


def breakdown_for_client(breakdown: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, bucket in breakdown.items():
        if not isinstance(bucket, dict):
            continue
        findings = bucket.get("findings") or []
        sanitized = [sanitize_finding(f) for f in findings if isinstance(f, dict)]
        out[key] = {
            "score": bucket.get("score"),
            "finding_count": bucket.get("finding_count", len(sanitized)),
            "findings": sanitized,
        }
    return out


def breakdown_for_storage(breakdown: dict[str, Any]) -> dict[str, Any]:
    """Counts and scores only — safe for jsonb column."""
    out: dict[str, Any] = {}
    for key, bucket in breakdown.items():
        if not isinstance(bucket, dict):
            continue
        out[key] = {
            "score": bucket.get("score"),
            "finding_count": bucket.get("finding_count", 0),
        }
    return out


def build_web_scan_result(scored: dict[str, Any], *, source_label: str) -> dict[str, Any]:
    breakdown = scored.get("breakdown") or {}
    client_breakdown = breakdown_for_client(breakdown)
    finding_count = sum(int(b.get("finding_count", 0)) for b in client_breakdown.values())
    return {
        "source_label": source_label,
        "overall_score": scored.get("overall_score"),
        "grade": scored.get("grade"),
        "summary": scored.get("summary"),
        "breakdown": client_breakdown,
        "finding_count": finding_count,
        "storage_breakdown": breakdown_for_storage(breakdown),
        "rules_load_warnings": scored.get("rules_load_warnings") or [],
        "vibe_stage": scored.get("vibe_stage"),
        "vibe_stage_title": scored.get("vibe_stage_title"),
        "vibe_stage_lesson": scored.get("vibe_stage_lesson"),
        "priority_fixes": scored.get("priority_fixes") or [],
        "detailed_report": scored.get("detailed_report"),
        "coach_prompt": scored.get("coach_prompt"),
    }


def validate_upload_code(code: str) -> None:
    if not code or not code.strip():
        raise ValueError("Code snippet is empty.")
    if len(code.encode("utf-8")) > _MAX_CODE_BYTES:
        raise ValueError("Code exceeds 2MB limit.")
