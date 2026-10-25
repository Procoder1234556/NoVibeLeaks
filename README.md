# NoVibeLeaks

**MCP server for agent-loop security** — catch hardcoded secrets, risky MCP configs, and vibe-coding mistakes in Cursor, Claude Code, and any MCP host.

[![MCP Registry](https://img.shields.io/badge/listing-io.github.Procoder1234556%2Fnovibeleaks-6264FF.svg)](https://registry.modelcontextprotocol.io/)
[![PyPI](https://img.shields.io/pypi/v/novibeleaks.svg?label=novibeleaks)](https://pypi.org/project/novibeleaks/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](secmcp/pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<!-- mcp-name: io.github.Procoder1234556/novibeleaks -->

| Install | Command |
|---------|---------|
| **Marketplace / registry** | Search **NoVibeLeaks** in your IDE’s MCP catalog (`io.github.Procoder1234556/novibeleaks`) |
| **Manual** | `uvx novibeleaks` in `mcp.json` |

Full marketplace steps: **[MARKETPLACE.md](./MARKETPLACE.md)**

---

## `mcp.json`

```json
{
  "mcpServers": {
    "novibeleaks": {
      "command": "uvx",
      "args": ["novibeleaks"]
    }
  }
}
```

## Tools

| Tool | Purpose |
|------|---------|
| `check_secrets` | Tokens and keys in code or files |
| `validate_api_key` | Live provider check (masked) |
| `scan_vibe_bugs` | Config and LLM anti-patterns |
| `get_security_score` | Weighted 0–100 + breakdown |
| `list_available_rules` | YAML rule catalog |

## Develop from source

```bash
git clone https://github.com/Procoder1234556/NoVibeLeaks.git
cd NoVibeLeaks/secmcp
uv sync
uv run mcp dev server.py
pytest -q
```

## Registry metadata

[`server.json`](./server.json) is the canonical MCP Registry entry (PyPI package `novibeleaks`, stdio transport).

## More in this repo (optional)

CI scanner (`scripts/scan_repository.py`), SARIF export, and a small Next.js demo (`secmcp-web/`) are **not** required to use the MCP server.

## License

MIT — [LICENSE](LICENSE)
