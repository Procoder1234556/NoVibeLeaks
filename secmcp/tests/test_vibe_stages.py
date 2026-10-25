"""Vibe-stage narrative on scan outputs."""

from __future__ import annotations

from secmcp.scanner import check_secrets_sync, security_score_async
from secmcp.vibe_stages import build_vibe_report
import asyncio


def test_openai_secret_maps_to_stage_6():
    out = check_secrets_sync(code='OPENAI = "sk-abcdefghijklmnopqrstuvwxyz123456"')
    assert out["count"] >= 1
    assert out["vibe_stage"] >= 5
    assert "detailed_report" in out
    assert "Stage" in out["detailed_report"]
    assert out["findings"][0].get("vibe_stage") in (5, 6)


def test_clean_snippet_high_stage():
    report = build_vibe_report(findings=[], text="def hello(): return 1", overall_score=95.0, grade="A")
    assert report["vibe_stage"] == 15


def test_security_score_includes_coach_fields():
    scored = asyncio.run(
        security_score_async(code='key = "sk-abcdefghijklmnopqrstuvwxyz123456"', path="t.py")
    )
    assert scored.get("coach_prompt")
    assert scored.get("priority_fixes")
    assert "findings" in scored
    assert scored["count"] >= 1
    assert "execution_summary" in scored
    assert "Score breakdown" in scored["detailed_report"]
