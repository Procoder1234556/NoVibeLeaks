# Technology Stack — SecMCP

**Last Updated:** 2025-10-25  
**Version:** 1.0  

## 1. Stack Overview

| Layer | Phase 1 (now) | Phase 2 | Phase 3 |
|-------|---------------|---------|---------|
| Agent interface | MCP stdio (FastMCP) | — | — |
| Core logic | Python 3.11+ package `secmcp` | Same via Action script | API subprocess or shared wheel |
| Rules | YAML (PyYAML) | Same | Same + DB metadata optional |
| HTTP | httpx async | httpx | httpx / fetch |
| CI | — | GitHub Actions | — |
| Web | — | — | Next.js 15, Supabase |

**Architecture:** Monolithic Python scanner library + thin MCP adapter; no microservices in MVP.

---

## 2. MCP Server (Phase 1)

| Component | Choice | Version pin (minimum) | Why |
|-----------|--------|------------------------|-----|
| Language | Python | 3.11+ | MCP SDK, fast scripting |
| MCP SDK | `mcp[cli]` | ≥ 1.0 (tested 1.27) | Official protocol, Inspector |
| Server API | FastMCP (`mcp.server.fastmcp`) | bundled | `@mcp.tool()` decorators |
| YAML | PyYAML | ≥ 6.0 | Safe load only |
| HTTP client | httpx | ≥ 0.27 | Async provider checks |
| Package mgr | uv (recommended) or pip | — | `uv run mcp dev server.py` |

### Entrypoint

- `../secmcp/server.py` — registers 5 tools, `mcp.run()` stdio

### Install (canonical)

```bash
cd "../secmcp"
pip install "mcp[cli]" pyyaml httpx
# or: uv sync
```

### MCP client config (Cursor)

```json
{
  "mcpServers": {
    "secmcp": {
      "command": "python",
      "args": ["<ABS_PATH>/secmcp/server.py"],
      "cwd": "<ABS_PATH>/secmcp"
    }
  }
}
```

Prefer **python + path** over `npx @latest` for supply-chain stability (see MCP_SECURITY_CHECKLIST).

---

## 3. Rules Engine

| Item | Detail |
|------|--------|
| Location | `../secmcp/rules/*.yaml` |
| Schema | `rules[]` with `name`, `severity`, `pattern`, `message`, optional `category`, `recommendation` |
| Execution | **Regex only** — no `exec` from YAML |
| Loader | `secmcp.rules_loader` — multi-file, skip invalid rules with warnings |

---

## 4. API Key Validation

| Provider | Endpoint style | Notes |
|----------|----------------|-------|
| OpenAI | GET /v1/models | Bearer |
| Anthropic | GET /v1/models | x-api-key header |
| Stripe | GET /v1/balance | Basic auth |
| GitHub | GET /user | Bearer PAT |
| Supabase | GET `{url}/rest/v1/` | needs `supabase_url` |
| AWS | STS GetCallerIdentity | SigV4, needs secret |

Cache: in-memory SHA-256 keyed, ~120s TTL.  
Never persist raw keys.

---

## 5. GitHub Action (Phase 2 — planned)

| Item | Choice |
|------|--------|
| Runner | `ubuntu-latest` |
| Python | 3.11 |
| Auth | `GITHUB_TOKEN` (issues: write) |
| Scanner | `python -m secmcp.scanner` or thin `scripts/scan_repo.py` |

---

## 6. Web Dashboard (Phase 3 — planned)

| Component | Choice | Version target |
|-----------|--------|----------------|
| Framework | Next.js | 15.x App Router |
| DB + Auth | Supabase | Postgres + Auth |
| Hosting | Vercel | — |
| API | Route Handler calling Python or ported TS scanner | TBD |

---

## 7. Context7 MCP (mandatory for agents, not runtime dep)

| Tool | Purpose |
|------|---------|
| `resolve-library-id` | Map package name → `/org/project` id |
| `query-docs` | Current API/docs for MCP, Next, Supabase, Actions, httpx |

**Policy:** Every [AGENT_PROMPTS.md](./AGENT_PROMPTS.md) run starts with Context7 per [CONTEXT7_MCP.md](./CONTEXT7_MCP.md).

Pre-resolved IDs include `/modelcontextprotocol/python-sdk`, `/vercel/next.js/v15.1.11`, `/supabase/supabase`, `/encode/httpx`, `/websites/github_en_actions`.

---

## 8. Agent Skills (optional, not runtime deps)

| Skill | Purpose |
|-------|---------|
| vercel-labs/skills@find-skills | Discover skills |
| github/awesome-copilot@mcp-security-audit | MCP JSON audit |
| github/awesome-copilot@secret-scanning | Secret patterns |

See [SKILLS_SETUP.md](./SKILLS_SETUP.md).

---

## 9. Environment Variables

### SecMCP server

None required for local secret/vibe scans.  
Optional: none for MCP process (keys passed only in tool args by agent—discourage logging).

### Phase 3 (future)

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` (server only)
- Scan API secrets as needed

---

## 10. Security & Compliance

- No storage of user code beyond request lifetime (Phase 1 MCP)
- Masked keys in all validation responses
- Pin MCP launch command; audit with checklist
- OWASP-aligned messaging for vibe bugs (TLS, eval, SQL formatting)

---

## 11. Update Policy

- Patch `mcp` minor versions after Inspector smoke test
- Rule changes: semver tag on rules pack later; MVP edits `default-rules.yaml` directly
- Next.js major: follow Vercel migration guides when Phase 3 starts
