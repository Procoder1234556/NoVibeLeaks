"""Optional leakferret binary adapter (L4 RFC stub)."""

from secmcp.leakferret_adapter import (
    baseline_diff_via_leakferret,
    leakferret_available,
    verify_finding_via_leakferret,
)


def test_leakferret_unavailable_without_env(monkeypatch) -> None:
    monkeypatch.delenv("SECMCP_LEAKFERRET_BIN", raising=False)
    assert leakferret_available() is False
    out = verify_finding_via_leakferret({"rule": "openai_api_key"})
    assert out["available"] is False
    assert "SECMCP_LEAKFERRET_BIN" in out["error"]


def test_leakferret_stub_when_binary_path_set(tmp_path, monkeypatch) -> None:
    fake_bin = tmp_path / "leakferret-mcp"
    fake_bin.write_text("", encoding="utf-8")
    monkeypatch.setenv("SECMCP_LEAKFERRET_BIN", str(fake_bin))
    assert leakferret_available() is True
    out = baseline_diff_via_leakferret(tmp_path)
    assert out["available"] is False
    assert "not implemented" in out["error"]
