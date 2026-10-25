"""MCP config scans must not fire on documentation that mentions mcpServers."""

from secmcp.mcp_config import scan_mcp_config_text
from secmcp.scanner import scan_vibe_bugs_sync


def test_markdown_with_backticks_not_scanned_as_mcp_config() -> None:
    doc = """# MCP setup

Use `mcpServers` in Cursor. Example backtick: `curl https://example.com`.

```json
{ "note": "not root mcpServers — fenced block should not enable whole-file scan" }
```
"""
    assert scan_mcp_config_text(doc, "docs/MCP_SECURITY_CHECKLIST.md") == []


def test_valid_mcp_json_still_scanned_when_not_canonical_path(tmp_path) -> None:
    config = tmp_path / "custom-config.json"
    config.write_text(
        '{"mcpServers": {"x": {"command": "bash", "args": ["-c", "echo $(whoami)"]}}}',
        encoding="utf-8",
    )
    text = config.read_text(encoding="utf-8")
    findings = scan_mcp_config_text(text, str(config))
    rules = {f["rule"] for f in findings}
    assert "mcp_args_shell_injection" in rules


def test_scan_vibe_bugs_skips_docs_mentioning_mcp_servers() -> None:
    doc = "See mcpServers and `$(rm -rf /)` in security checklist prose.\n"
    out = scan_vibe_bugs_sync(code=doc, path="skills/checklist.md")
    mcp_rules = {f["rule"] for f in out["findings"] if str(f["rule"]).startswith("mcp_")}
    assert mcp_rules == set()
