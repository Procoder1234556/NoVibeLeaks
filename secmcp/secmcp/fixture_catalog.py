"""Suppress findings on known documentation fixture literals (YAML data only)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_CATALOG_PATH = Path(__file__).resolve().parent / "fixture_catalog.yaml"


@dataclass(frozen=True)
class FixtureCatalog:
    exact_literals: frozenset[str]
    line_markers: frozenset[str]

    def line_is_fixture(self, line: str) -> bool:
        for literal in self.exact_literals:
            if literal in line:
                return True
        upper = line.upper()
        for marker in self.line_markers:
            token = marker.upper()
            # Avoid substring false positives (e.g. "EXAMPLE" inside fake_example_key).
            if token in upper and (
                upper == token
                or f"_{token}_" in upper
                or upper.startswith(f"{token}_")
                or upper.endswith(f"_{token}")
                or f"-{token}-" in upper
            ):
                return True
        return False


@lru_cache(maxsize=1)
def load_fixture_catalog() -> FixtureCatalog:
    if not _CATALOG_PATH.is_file():
        return FixtureCatalog(frozenset(), frozenset())
    data = yaml.safe_load(_CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return FixtureCatalog(frozenset(), frozenset())
    exact = data.get("exact_literals") or []
    markers = data.get("line_markers") or []
    return FixtureCatalog(
        exact_literals=frozenset(str(x) for x in exact if x),
        line_markers=frozenset(str(x) for x in markers if x),
    )


def filter_fixture_findings(text: str, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop findings whose source line matches the static fixture catalog."""
    catalog = load_fixture_catalog()
    if not catalog.exact_literals and not catalog.line_markers:
        return findings
    lines = text.splitlines()
    kept: list[dict[str, Any]] = []
    for finding in findings:
        line_no = int(finding.get("location", {}).get("line", 0))
        if line_no < 1 or line_no > len(lines):
            kept.append(finding)
            continue
        if catalog.line_is_fixture(lines[line_no - 1]):
            continue
        kept.append(finding)
    return kept
