# NoVibeLeaks (Python package: `novibeleaks`)

> **Full project overview:** see the repository root [`README.md`](../README.md).

<!-- mcp-name: io.github.Procoder1234556/novibeleaks -->

Security MCP for AI-assisted coding: **hardcoded secrets**, **API key validation**, and **common LLM anti-patterns** — five tools for Cursor, Claude Code, and any MCP host.

## Quick install (&lt; 3 minutes)

### 1. Dependencies

From this directory:

```bash
uv sync
# or: pip install -e ".[cli]"  with mcp[cli] from pyproject
```

### 2. Run locally (MCP Inspector)

```bash
uv run mcp dev server.py
```

### 3. Cursor / Claude Code (stdio)

Copy [`.cursor/mcp.json.example`](../.cursor/mcp.json.example) to your user or project MCP config and set `REPLACE_WITH_ABSOLUTE_PATH` to this repo.

Add to MCP config (adjust path):

```json
{
  "mcpServers": {
    "secmcp": {
      "command": "uv",
      "args": ["run", "--directory", "D:/cybersecurity mcp server/secmcp", "python", "server.py"]
    }
  }
}
```

Or with plain Python:

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

## MCP tools

| Tool | Purpose |
|------|---------|
| `check_secrets` | Regex + YAML rules for tokens/keys |
| `validate_api_key` | Live check (OpenAI, Anthropic, Stripe, Supabase, GitHub, AWS) |
| `scan_vibe_bugs` | Configuration + code-quality anti-patterns |
| `get_security_score` | Weighted 0–100 score + breakdown |
| `list_available_rules` | Loaded rule catalog |

All findings include **severity**, **message**, **location**, and **recommendation**.

## Rules

Declarative YAML only — no code execution from rules. Defaults live in `rules/default-rules.yaml`. Drop more `*.yaml` files in `rules/` to extend (restart server to reload).

## API key validation

- Full keys are **never** logged or returned (masked like `sk-a…xyz9`).
- Results: `valid` | `invalid` | `rate_limited` | `network_error` | `unknown`.
- Short in-memory cache (~2 min) to respect provider rate limits.
- **Supabase**: pass `supabase_url` (project REST base).
- **AWS**: pass access key id as `key` and `aws_secret` for STS check.

### `validate_keys` cost

`validate_api_key` and `get_security_score` with `validate_keys=True` may call provider APIs **once per detected key pattern** in the snippet. Large files with many matches can add seconds of latency and hit rate limits; the web dashboard and `scan_snippet.py` default to `validate_keys=False`. Use live validation only when you need confirmation, not on full-repo CI walks.

## Project layout

```
secmcp/
├── server.py              # MCP entry (FastMCP / MCPServer)
├── rules/default-rules.yaml
├── secmcp/                # Shared library (GitHub Action + web later)
│   ├── scanner.py
│   ├── secrets.py
│   ├── api_keys.py
│   ├── vibe_bugs.py
│   ├── scoring.py
│   └── rules_loader.py
├── pyproject.toml
└── README.md
```

## Self-check

```bash
uv run python -m secmcp.rules_loader
uv run python -m secmcp.scanner
```

**Prompt K parity** (vs vendored mcp-guard unsafe fixture):

```bash
pip install -e ../vendor/mcp-guard
pip install -e ".[dev]"
pytest tests/test_parity_mcp_guard.py -v
```

## Upstream references

Patterns from **[mcp-guard](https://github.com/chiragborse1/mcp-guard)** (MIT, cloned under `../vendor/mcp-guard`) power MCP config checks in `secmcp/mcp_config.py` and `rules/mcp-guard-patterns.yaml`. **[leakferret](https://github.com/leakferrethq/leakferret)** is vendored for verify/rewrite ideas — see `prompts-directory-main/VENDOR_LANDSCAPE.md`.

## Production design

Scaling and resilience notes (caching, rate limits, fault tolerance, monolith boundaries) live in [`docs/PRODUCTION_DESIGN.md`](docs/PRODUCTION_DESIGN.md). Agent skill: `.agents/skills/production-system-design/`.

## Roadmap

- **Phase 2**: `.github/workflows/secmcp.yml` daily scan + issues
- **Phase 3**: Next.js dashboard + Supabase history
