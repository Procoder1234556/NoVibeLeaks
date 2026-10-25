# MCP config security checklist (SecMCP + mcp-security-audit)

Use when adding **SecMCP** or any MCP server to `.cursor/mcp.json`, `.mcp.json`, or Claude Code config.

## Before merge

- [ ] **No hardcoded secrets** in `args` or `env` (use host env vars, not literal `sk-…` / `ghp_…`).
- [ ] **No shell injection** in args: no `$(...)`, backticks, `;`, `|`, `&&`, `bash -c`, `curl | sh`.
- [ ] **Pinned launchers**: prefer `uv run` / `python path/to/server.py` over bare `npx package` without exact version.
- [ ] **SecMCP path** points to repo `secmcp/server.py` with fixed `cwd`.
- [ ] **Least privilege**: SecMCP does not need network except `validate_api_key` (document when offline).
- [ ] Run SecMCP `check_secrets` on config JSON if unsure.

## Good SecMCP entry

```json
{
  "mcpServers": {
    "secmcp": {
      "command": "python",
      "args": ["D:/cybersecurity mcp server/secmcp/server.py"],
      "cwd": "D:/cybersecurity mcp server/secmcp"
    }
  }
}
```

## Bad patterns

```json
{
  "mcpServers": {
    "bad": {
      "command": "npx",
      "args": ["-y", "some-mcp@latest", "--api-key", "sk-real-key-here"]
    }
  }
}
```

## Severity mapping (audit reports)

| Audit severity | SecMCP equivalent |
|----------------|-------------------|
| CRITICAL | critical |
| HIGH | high |
| MEDIUM | medium |
| LOW / INFO | low |

Full reference: [awesome-copilot mcp-security-audit](https://skills.sh/github/awesome-copilot/mcp-security-audit).
