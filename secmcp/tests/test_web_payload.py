"""Phase 3 web payload sanitization."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from secmcp.web_payload import breakdown_for_storage, sanitize_finding, validate_upload_code

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_SCRIPT = REPO_ROOT / "scripts" / "scan_snippet.py"


def test_sanitize_finding_strips_raw_match():
    raw = {
        "rule": "openai_api_key",
        "severity": "critical",
        "category": "secrets",
        "message": "OpenAI key",
        "matched": "sk-secretvalue",
        "location": {"file": "x.py", "line": 3, "column": 1},
    }
    out = sanitize_finding(raw)
    assert "matched" not in out
    assert out["location"]["line"] == 3


def test_breakdown_for_storage_omits_findings():
    breakdown = {
        "secrets": {"score": 75.0, "finding_count": 1, "findings": [{"rule": "x"}]},
    }
    stored = breakdown_for_storage(breakdown)
    assert stored["secrets"] == {"score": 75.0, "finding_count": 1}
    assert "findings" not in stored["secrets"]


def test_validate_upload_code_rejects_empty():
    try:
        validate_upload_code("   ")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_scan_snippet_script_detects_secret():
    payload = json.dumps({"code": 'key = "sk-abcdefghijklmnopqrstuvwxyz123456"', "label": "t.py"})
    proc = subprocess.run(
        [sys.executable, str(SCAN_SCRIPT), "--stdin-json"],
        input=payload,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT / "secmcp"),
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT / "secmcp")},
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["overall_score"] < 100
    assert data["finding_count"] >= 1
    assert "storage_breakdown" in data
