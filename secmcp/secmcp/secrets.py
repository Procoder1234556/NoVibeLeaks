"""Secret detection via declarative rules."""

from __future__ import annotations

from typing import Any

from secmcp.fixture_catalog import filter_fixture_findings
from secmcp.rules_loader import Rule

_SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _dedupe_secret_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One finding per line; prefer named rules over generic_secret_assignment (mcp-guard-style)."""
    by_line: dict[int, dict[str, Any]] = {}
    for finding in findings:
        line = int(finding["location"]["line"])
        current = by_line.get(line)
        if current is None:
            by_line[line] = finding
            continue
        if finding["rule"] == "generic_secret_assignment" and current["rule"] != "generic_secret_assignment":
            continue
        if current["rule"] == "generic_secret_assignment" and finding["rule"] != "generic_secret_assignment":
            by_line[line] = finding
            continue
        if _SEVERITY_RANK.get(finding["severity"], 9) < _SEVERITY_RANK.get(current["severity"], 9):
            by_line[line] = finding
    return sorted(by_line.values(), key=lambda item: item["location"]["line"])


def scan_secrets(text: str, source: str, rules: list[Rule]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    secret_rules = [r for r in rules if r.category == "secrets"]
    for rule in secret_rules:
        findings.extend(rule.find_in(text, source))
    findings = _dedupe_secret_findings(findings)
    return filter_fixture_findings(text, findings)
