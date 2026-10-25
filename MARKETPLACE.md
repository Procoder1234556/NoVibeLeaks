# NoVibeLeaks — MCP Marketplace listing

NoVibeLeaks is distributed as a **stdio MCP server** via the [official MCP Registry](https://registry.modelcontextprotocol.io/). Cursor, Claude, and other clients ingest the registry to populate their MCP marketplaces.

| Field | Value |
|-------|--------|
| **Registry name** | `io.github.Procoder1234556/novibeleaks` |
| **PyPI package** | [`novibeleaks`](https://pypi.org/project/novibeleaks/) |
| **Run command** | `uvx novibeleaks` (or `novibeleaks` after `pip install novibeleaks`) |
| **Metadata file** | [`server.json`](./server.json) |

## Install in Cursor (after registry listing)

1. Open **Cursor Settings → MCP** (or **Features → MCP**).
2. Choose **Add server** / browse the **MCP directory** (registry-backed catalog).
3. Search for **NoVibeLeaks** or `io.github.Procoder1234556/novibeleaks`.
4. Install — the client should run `uvx novibeleaks` over stdio.

### Manual `mcp.json` (same server)

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

Requires **Python 3.11+** and [uv](https://docs.astral.sh/uv/) on your PATH (for `uvx`).

## MCP tools (five)

| Tool | Purpose |
|------|---------|
| `check_secrets` | Hardcoded tokens and keys |
| `validate_api_key` | Live provider check (masked) |
| `scan_vibe_bugs` | Config / LLM anti-patterns |
| `get_security_score` | 0–100 score + breakdown |
| `list_available_rules` | YAML rule catalog |

No API keys are required to run secret and vibe scans. Live key validation uses keys you pass into the tool, not environment variables.

## Maintainer: go live on the registry

1. **Publish PyPI** (version must match `server.json`):
   - One-time: [docs/PYPI_ONE_TIME_SETUP.md](./docs/PYPI_ONE_TIME_SETUP.md) (trusted publisher — no token in repo).
   - Then: GitHub **Actions → Publish PyPI → Run workflow**.

2. **Publish registry metadata** (GitHub namespace auth):

   ```bash
   npm install -g mcp-publisher
   mcp-publisher login github
   mcp-publisher publish ./server.json
   ```

   Or run the GitHub Action **Publish MCP Registry** (repository secret `PYPI_API_TOKEN` for PyPI; registry auth via `mcp-publisher login` locally first time).

3. Wait for marketplace sync (aggregators may cache up to ~1 hour).

See also [docs/MCP_REGISTRY.md](./docs/MCP_REGISTRY.md) and **[docs/MCPMARKET.md](./docs/MCPMARKET.md)** (your [HUB connect](https://app.mcpmarket.com/p03490978/connect) link).
