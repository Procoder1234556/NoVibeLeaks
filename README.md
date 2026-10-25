<p align="center">
  <img src="assets/logo.svg" width="96" alt="NoVibeLeaks logo" />
</p>

<h1 align="center">NoVibeLeaks</h1>

<p align="center">
  <strong>Security MCP for vibe-coded apps.</strong><br/>
  Catch secrets and anti-patterns in the agent loop — before they ship.
</p>

<p align="center">
  <a href="https://github.com/Procoder1234556/NoVibeLeaks/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Procoder1234556/NoVibeLeaks/ci.yml?branch=main&label=tests" alt="CI"/></a>
  <a href="https://pypi.org/project/novibeleaks/"><img src="https://img.shields.io/pypi/v/novibeleaks?label=PyPI" alt="PyPI"/></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-stdio-6264FF" alt="MCP"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"/></a>
</p>

<p align="center">
  Registry: <code>io.github.Procoder1234556/novibeleaks</code>
</p>

<!-- mcp-name: io.github.Procoder1234556/novibeleaks -->

---

<p align="center">
  <img src="assets/architecture.svg" alt="NoVibeLeaks architecture: MCP host to five tools and YAML rules" width="100%"/>
</p>

## What it does

NoVibeLeaks is a **Model Context Protocol** server (Python, stdio). Your coding agent calls five tools while it writes code — same idea as a focused package in [Ponytail’s `ponytail-mcp`](https://github.com/DietrichGebert/ponytail/tree/main/ponytail-mcp), but for **secrets, MCP config risk, and LLM anti-patterns**.

| Tool | Purpose |
|------|---------|
| `check_secrets` | Hardcoded API keys, tokens, private keys |
| `validate_api_key` | Optional live provider check (masked) |
| `scan_vibe_bugs` | Debug flags, CORS, auth gaps, risky patterns |
| `get_security_score` | 0–100 score + category breakdown |
| `list_available_rules` | Loaded YAML rule catalog |

```mermaid
flowchart LR
  H[IDE / Agent] <-->|stdio MCP| S[NoVibeLeaks]
  S --> R[(YAML rules)]
  S --> F[Findings + score]
```

## Install

**PyPI / uvx** (recommended after publish):

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

**From this repo** (development):

```bash
cd secmcp
uv sync
uv run mcp dev server.py
```

Copy [`.cursor/mcp.json.example`](.cursor/mcp.json.example) for local paths.

## Repo layout (MCP only)

```
NoVibeLeaks/
├── README.md
├── server.json          # MCP Registry manifest
├── secmcp/              # Python package + server.py + rules/
├── assets/              # README diagrams
└── .github/workflows/   # test + PyPI publish
```

## Registry & marketplace

| Goal | Doc |
|------|-----|
| Official MCP Registry | [docs/MCP_REGISTRY.md](docs/MCP_REGISTRY.md) |
| MCPmarket listing | [docs/MCPMARKET.md](docs/MCPMARKET.md) |

## Develop

```bash
cd secmcp && uv sync && pytest -q
```

## License

MIT — [LICENSE](LICENSE)
