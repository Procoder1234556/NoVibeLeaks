"""Common LLM-generated anti-patterns (rules outside secrets category)."""

from __future__ import annotations

from typing import Any

from secmcp.fixture_catalog import filter_fixture_findings
from secmcp.mcp_config import scan_mcp_config_text
from secmcp.rules_loader import Rule

# ponytail: extra inline patterns until community YAML grows
_BUILTIN: list[tuple[str, str, str, str]] = [
    (
        "dangerously_set_inner_html",
        "high",
        "React dangerouslySetInnerHTML without sanitization is XSS-prone.",
        "Sanitize HTML (DOMPurify) or avoid raw HTML injection.",
    ),
    (
        "pickle_untrusted",
        "high",
        "pickle.loads on untrusted data allows arbitrary code execution.",
        "Use JSON or other safe serializers for untrusted input.",
    ),
]


def scan_vibe_bugs(text: str, source: str, rules: list[Rule]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    findings.extend(scan_mcp_config_text(text, source))
    for rule in rules:
        if rule.category == "secrets":
            continue
        findings.extend(rule.find_in(text, source))

    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        lower = line.lower()
        if "dangerouslysetinnerhtml" in lower.replace(" ", ""):
            findings.append(
                _finding(
                    "dangerously_set_inner_html",
                    "high",
                    "configuration",
                    _BUILTIN[0][2],
                    _BUILTIN[0][3],
                    source,
                    i,
                    1,
                )
            )
        if "pickle.loads" in line:
            findings.append(
                _finding(
                    "pickle_untrusted",
                    "high",
                    "code_quality",
                    _BUILTIN[1][2],
                    _BUILTIN[1][3],
                    source,
                    i,
                    1,
                )
            )
    findings = _dedupe(findings)
    return filter_fixture_findings(text, findings)


def _finding(
    rule: str,
    severity: str,
    category: str,
    message: str,
    recommendation: str,
    source: str,
    line: int,
    column: int,
) -> dict[str, Any]:
    return {
        "rule": rule,
        "severity": severity,
        "category": category,
        "message": message,
        "recommendation": recommendation,
        "location": {"file": source, "line": line, "column": column},
    }


def _dedupe(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, int, str]] = set()
    out: list[dict[str, Any]] = []
    for f in findings:
        loc = f.get("location") or {}
        key = (str(f.get("rule")), int(loc.get("line", 0)), str(loc.get("file", "")))
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out
