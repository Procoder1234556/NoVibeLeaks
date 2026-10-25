# NoVibeLeaks

**Stop secret leaks in vibe-coded apps** — a security-first [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for Cursor, Claude Code, and any MCP host. Catch hardcoded keys, risky MCP configs, and common AI-generated mistakes **while the agent writes code**, not after deploy.

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](secmcp/pyproject.toml)
[![MCP Registry](https://img.shields.io/badge/MCP-Registry-6264FF.svg)](https://registry.modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/Procoder1234556/NoVibeLeaks/secmcp-ci.yml?branch=main&label=tests)](https://github.com/Procoder1234556/NoVibeLeaks/actions)

<!-- mcp-name: io.github.Procoder1234556/novibeleaks -->

**Registry name:** `io.github.Procoder1234556/novibeleaks` · **PyPI:** [`novibeleaks`](https://pypi.org/project/novibeleaks/)

---

## Why NoVibeLeaks?

Coding agents move fast. They paste API keys, weaken MCP server configs, and leave debug paths enabled. Heavy enterprise SAST is slow; chat-regex is fragile.

**NoVibeLeaks** sits in the **agent loop**:

| Benefit | Detail |
|---------|--------|
| **YAML rules** | Declarative patterns — no arbitrary code execution from rule files |
| **Same engine** | MCP tools and `scripts/scan_repository.py` share one scanner |
| **Actionable output** | Severity, file:line, and fix guidance on every finding |
| **Optional live checks** | Validate provider keys with masked responses |

---

## Features

- **Secrets** — OpenAI, Anthropic, AWS, GitHub, Stripe, and more via regex + YAML
- **MCP config** — Patterns aligned with [mcp-guard](vendor/mcp-guard/) (unsafe servers, env leakage)
- **Vibe bugs** — Debug flags, permissive CORS, missing auth, LLM anti-patterns
- **API key validation** — OpenAI, Anthropic, Stripe, Supabase, GitHub, AWS (masked)
- **Security score** — Weighted 0–100 with category breakdown
- **CI** — Repo walk, `.mcpguardignore`, SARIF export, scheduled GitHub issues
- **Web dashboard** — Optional Next.js UI (`secmcp-web/`) with Supabase history

---

## Quick start

**Requirements:** Python **3.11+**, [uv](https://docs.astral.sh/uv/) (recommended) or pip.

### Install from PyPI (recommended)

```bash
pip install novibeleaks
# or: uvx novibeleaks   (stdio MCP — configure in your host)
```

### Install from source

```bash
git clone https://github.com/Procoder1234556/NoVibeLeaks.git
cd NoVibeLeaks/secmcp
uv sync
uv run mcp dev server.py
```

### Cursor / Claude Code (`mcp.json`)

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

From a local clone (no PyPI):

```json
{
  "mcpServers": {
    "novibeleaks": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/NoVibeLeaks/secmcp", "python", "server.py"]
    }
  }
}
```

See [`.cursor/mcp.json.example`](.cursor/mcp.json.example).

---

## MCP tools (five)

| Tool | Purpose |
|------|---------|
| `check_secrets` | Detect tokens and keys in a snippet or file |
| `validate_api_key` | Live provider check; secrets never echoed back |
| `scan_vibe_bugs` | Config and code-quality anti-patterns |
| `get_security_score` | Weighted score + category breakdown |
| `list_available_rules` | Loaded YAML rule catalog |

---

## Repository scanning

```bash
python scripts/scan_repository.py .
python scripts/scan_repository.py . --sarif results.sarif --no-fail
```

Daily GitHub workflow: [`.github/workflows/secmcp.yml`](.github/workflows/secmcp.yml).

---

## Project layout

```
NoVibeLeaks/
├── secmcp/              # MCP server + Python package (PyPI: novibeleaks)
├── secmcp-web/          # Optional Next.js dashboard
├── scripts/             # CI scan + SARIF helpers
├── server.json          # Official MCP Registry metadata
├── vendor/              # Upstream references (mcp-guard, leakferret)
└── .github/workflows/   # CI, web, release
```

---

## Development

```bash
cd secmcp
uv sync
pytest -q
```

Contributing: [CONTRIBUTING.md](CONTRIBUTING.md) · Security: [SECURITY.md](SECURITY.md) · Registry publish: [docs/MCP_REGISTRY.md](docs/MCP_REGISTRY.md)

---

## Acknowledgments

Built with ideas from [mcp-guard](https://github.com/chiragborse1/mcp-guard) (MIT) and [leakferret](https://github.com/leakferrethq/leakferret) (Apache-2.0) under `vendor/`.

---

## License

MIT — see [LICENSE](LICENSE). Third-party code in `vendor/` remains under upstream licenses.
