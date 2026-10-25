"""Web/API payload sanitization (library)."""

from __future__ import annotations

from secmcp.web_payload import breakdown_for_storage, sanitize_finding, validate_upload_code


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
