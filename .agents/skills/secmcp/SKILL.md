---
name: secmcp
description: SecMCP playbook — five MCP tools, YAML rules, vendor parity (mcp-guard/leakferret). Use with Context7 and sibling skills in .agents/skills/.
---

# SecMCP agent skill

## Prerequisites (every session)

1. **brain.md** + **navigation.md** + **test.md** (pending TEST_LOG?)
2. **Context7** — `prompts-directory-main/CONTEXT7_MCP.md`
3. **SecMCP MCP** — `secmcp/server.py` in Cursor MCP config
4. **Vendor context** — `prompts-directory-main/VENDOR_STATUS.md`
5. **taskflow.md** — session type T1–T4

## MCP tools

| Tool | Use |
|------|-----|
| `check_secrets` | Source files, snippets, `.env` |
| `scan_vibe_bugs` | MCP configs, eval/TLS/CORS, **includes `mcp_config.py` checks** |
| `validate_api_key` | Masked live check (OpenAI, Anthropic, Stripe, Supabase*, GitHub, AWS*) |
| `get_security_score` | 0–100 + four buckets + **vibe stage** narrative |
| `list_available_rules` | YAML catalog (`default-rules.yaml`, `mcp-guard-patterns.yaml`) |

**Coach output (all scan tools):** `detailed_report` (markdown), `vibe_stage` (1–15), `priority_fixes`, `coach_prompt`, per-finding `vibe_stage` when mapped. Frame: Nikunj “15 stages of every vibe coder’s backend” + incremental fixes (no big-bang rewrite).

\* Supabase needs `supabase_url`; AWS needs `aws_secret`.

## Vendor: already merged

From **mcp-guard** (MIT, `vendor/mcp-guard/`):

- `secmcp/mcp_config.py` — MCP JSON env literals, injection patterns, npx pin warnings
- `rules/mcp-guard-patterns.yaml` — Postgres URL, Pinecone, Firecrawl

**Test fixture:** `vendor/mcp-guard/examples/unsafe-mcp-config/.cursor/mcp.json`

From **leakferret** (reference, `vendor/leakferret/`):

- `secmcp/fixture_catalog.yaml` — starter FP suppression for vendor doc literals (not full Rust catalog)

**Phase 2 CLI:** `python scripts/scan_repository.py [root]` (repo walk; same engines as MCP tools)

**Repo walk tests:** `pytest secmcp/tests/test_scan_repository.py` — parity count 7 on unsafe fixture; rules from YAML (`get_rules()`), not hardcoded matchers. No `GITHUB_TOKEN` in `.env` for tests; live GitHub validation is optional/env-only.

## Sibling skills (same `.agents/skills/` folder)

| Skill | Pair with SecMCP when |
|-------|------------------------|
| production-system-design | Phase 2/3 scale, CI bursts, validation rate limits (`secmcp/docs/PRODUCTION_DESIGN.md`) |
| mcp-security-audit | Auditing `.mcp.json` (static checklist + SecMCP scan) |
| secret-scanning | Setting up GHAS / push protection for Phase 2 |
| security-scan | Whole-PR review |
| mcp-server-security | Changing `server.py` or deployment |
| docs-guard | After porting vendor features — update VENDOR_STATUS |
| prompt-injection | Vibe apps accepting user content |

Routing table: `prompts-directory-main/AGENT_SKILL_ROUTING.md`

## Optional vendor CLI (parity / SARIF)

```bash
pip install -e vendor/mcp-guard
mcp-guard scan .cursor/mcp.json
```

Do not treat vendor output as source of truth over SecMCP for agent loops — prefer SecMCP MCP tools in-IDE.

## Rules

- Never log full API keys
- No code execution from YAML rules
- Update `VENDOR_STATUS.md` when porting more from `vendor/`
