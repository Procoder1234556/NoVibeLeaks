"""Benchmark-style score checks: clean snippet vs mcp-guard unsafe fixture."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from secmcp.scanner import check_secrets_sync, list_rules_summary, scan_repository_sync, security_score_async

REPO_ROOT = Path(__file__).resolve().parents[2]
UNSAFE_FIXTURE = REPO_ROOT / "vendor" / "mcp-guard" / "examples" / "unsafe-mcp-config"

CLEAN_CODE = '''
def health():
    return {"ok": True}
'''


def test_clean_snippet_scores_high() -> None:
    scored = asyncio.run(security_score_async(code=CLEAN_CODE))
    assert scored["overall_score"] >= 90
    assert scored["grade"] in {"A", "B"}
    assert "Score breakdown" in scored["detailed_report"]
    assert scored["execution_summary"]["finding_count"] == 0


def test_secret_snippet_scores_low() -> None:
    scored = asyncio.run(
        security_score_async(code='OPENAI = "sk-' + "a" * 48 + '"')
    )
    assert scored["count"] >= 1
    secrets_bucket = scored["breakdown"]["secrets"]["score"]
    assert secrets_bucket <= 75
    assert "Findings (detail)" in scored["detailed_report"]


@pytest.mark.skipif(not UNSAFE_FIXTURE.is_dir(), reason="mcp-guard fixture missing")
def test_unsafe_fixture_benchmark() -> None:
    repo = scan_repository_sync(UNSAFE_FIXTURE)
    assert repo["count"] == 7
    assert repo["overall_score"] < 75
    assert repo["grade"] in {"D", "F", "C", "B"}
    assert repo["files_scanned"] >= 2
    assert "Scan metadata" in repo["detailed_report"]


def test_rules_catalog_detailed_report() -> None:
    catalog = list_rules_summary()
    assert catalog["count"] >= 10
    assert "SecMCP rule catalog" in catalog["detailed_report"]
    assert catalog["execution_summary"]["rule_count"] == catalog["count"]


def test_check_secrets_has_execution_summary() -> None:
    out = check_secrets_sync(code='x = "sk-' + "b" * 48 + '"')
    assert out["execution_summary"]["finding_count"] >= 1
    assert out["severity_counts"].get("critical") or out["severity_counts"].get("high")
