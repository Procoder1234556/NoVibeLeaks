"""Load declarative YAML security rules (no code execution)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

VALID_SEVERITIES = frozenset({"critical", "high", "medium", "low"})
DEFAULT_CATEGORY = "secrets"


@dataclass(frozen=True)
class Rule:
    name: str
    severity: str
    pattern: str
    message: str
    recommendation: str
    category: str
    _compiled: re.Pattern[str]

    def find_in(self, text: str, source: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        for match in self._compiled.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            col = match.start() - text.rfind("\n", 0, match.start())
            findings.append(
                {
                    "rule": self.name,
                    "severity": self.severity,
                    "category": self.category,
                    "message": self.message,
                    "recommendation": self.recommendation,
                    "location": {
                        "file": source,
                        "line": line,
                        "column": max(col, 1),
                    },
                }
            )
        return findings


def _parse_rule(raw: dict[str, Any], source_file: str) -> Rule | None:
    try:
        name = str(raw["name"])
        severity = str(raw.get("severity", "medium")).lower()
        pattern = str(raw["pattern"])
        message = str(raw.get("message", f"Rule {name} matched."))
        recommendation = str(
            raw.get("recommendation", "Review this finding and remediate before shipping.")
        )
        category = str(raw.get("category", DEFAULT_CATEGORY)).lower()
    except (KeyError, TypeError):
        return None

    if severity not in VALID_SEVERITIES:
        severity = "medium"
    try:
        compiled = re.compile(pattern)
    except re.error:
        return None

    return Rule(
        name=name,
        severity=severity,
        pattern=pattern,
        message=message,
        recommendation=recommendation,
        category=category,
        _compiled=compiled,
    )


def load_rules_from_paths(paths: list[Path]) -> tuple[list[Rule], list[str]]:
    """Load rules from one or more YAML files. Returns (rules, errors)."""
    rules: list[Rule] = []
    errors: list[str] = []
    seen: set[str] = set()

    for path in paths:
        if not path.is_file():
            errors.append(f"Rules file not found: {path}")
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML in {path}: {e}")
            continue
        except OSError as e:
            errors.append(f"Cannot read {path}: {e}")
            continue

        if not isinstance(data, dict):
            errors.append(f"Invalid rules document in {path}: expected mapping with 'rules' key")
            continue
        raw_rules = data.get("rules")
        if raw_rules is None:
            errors.append(f"No 'rules' key in {path}")
            continue
        if not isinstance(raw_rules, list):
            errors.append(f"'rules' must be a list in {path}")
            continue

        for item in raw_rules:
            if not isinstance(item, dict):
                errors.append(f"Skipping non-object rule entry in {path}")
                continue
            rule = _parse_rule(item, path.name)
            if rule is None:
                errors.append(f"Skipping invalid rule in {path}: {item.get('name', '?')}")
                continue
            if rule.name in seen:
                continue
            seen.add(rule.name)
            rules.append(rule)

    return rules, errors


def default_rules_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "rules"


def load_default_rules() -> tuple[list[Rule], list[str]]:
    rules_dir = default_rules_dir()
    paths = sorted(rules_dir.glob("*.yaml")) + sorted(rules_dir.glob("*.yml"))
    if not paths:
        return [], [f"No YAML rules found in {rules_dir}"]
    return load_rules_from_paths(paths)


def demo() -> None:
    rules, errs = load_default_rules()
    assert rules, "expected default rules"
    assert not any("openai" in e for e in errs), errs
    sample = 'const k = "sk-abcdefghijklmnopqrstuvwxyz123456";'
    hits = [f for r in rules if r.name == "openai_api_key" for f in r.find_in(sample, "x.ts")]
    assert hits and hits[0]["severity"] == "critical"


if __name__ == "__main__":
    demo()
    print("rules_loader ok")
