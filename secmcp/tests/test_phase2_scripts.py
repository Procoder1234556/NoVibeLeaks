"""Phase 2 CI scripts: scan_repository.py and render_daily_issue.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_SCRIPT = REPO_ROOT / "scripts" / "scan_repository.py"
RENDER_SCRIPT = REPO_ROOT / "scripts" / "render_daily_issue.py"
UNSAFE_FIXTURE = REPO_ROOT / "vendor" / "mcp-guard" / "examples" / "unsafe-mcp-config"


def _run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_scan_repository_exits_nonzero_on_blocking_findings() -> None:
    if not UNSAFE_FIXTURE.is_dir():
        pytest.skip(f"mcp-guard unsafe fixture missing: {UNSAFE_FIXTURE}")
    proc = _run_script(SCAN_SCRIPT, str(UNSAFE_FIXTURE))
    assert proc.returncode == 1
    assert "findings" in proc.stdout.lower() or proc.returncode == 1


def test_scan_repository_no_fail_exits_zero() -> None:
    if not UNSAFE_FIXTURE.is_dir():
        pytest.skip(f"mcp-guard unsafe fixture missing: {UNSAFE_FIXTURE}")
    proc = _run_script(SCAN_SCRIPT, str(UNSAFE_FIXTURE), "--no-fail")
    assert proc.returncode == 0


def test_scan_repository_json_includes_score_fields(tmp_path: Path) -> None:
    if not UNSAFE_FIXTURE.is_dir():
        pytest.skip(f"mcp-guard unsafe fixture missing: {UNSAFE_FIXTURE}")
    out = tmp_path / "scan.json"
    proc = _run_script(
        SCAN_SCRIPT,
        str(UNSAFE_FIXTURE),
        "--json",
        "--no-fail",
    )
    assert proc.returncode == 0
    out.write_text(proc.stdout, encoding="utf-8")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "overall_score" in payload
    assert "grade" in payload


def test_render_daily_issue_writes_title_and_body(tmp_path: Path) -> None:
    scan_path = tmp_path / "scan-result.json"
    scan_path.write_text(
        json.dumps(
            {
                "count": 0,
                "severity_counts": {},
                "overall_score": 100.0,
                "grade": "A",
                "findings": [],
            }
        ),
        encoding="utf-8",
    )
    title_out = tmp_path / "title.txt"
    body_out = tmp_path / "body.md"
    proc = _run_script(
        RENDER_SCRIPT,
        str(scan_path),
        "--ref",
        "main",
        "--sha",
        "deadbeef",
        "--docs-url",
        "https://example.com/readme",
        "--title-out",
        str(title_out),
        "--body-out",
        str(body_out),
    )
    assert proc.returncode == 0
    title = title_out.read_text(encoding="utf-8").strip()
    body = body_out.read_text(encoding="utf-8")
    assert title == "[SecMCP] Daily scan — 0 findings"
    assert "deadbeef"[:7] in body
    assert "https://example.com/readme" in body


def test_render_daily_issue_missing_file_returns_2() -> None:
    proc = _run_script(RENDER_SCRIPT, str(REPO_ROOT / "nonexistent-scan.json"))
    assert proc.returncode == 2
    assert "Missing scan JSON" in proc.stderr
