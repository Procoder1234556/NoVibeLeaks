# Parity: SecMCP vs mcp-guard

**Date:** 2025-10-25  
**Fixture:** `vendor/mcp-guard/examples/unsafe-mcp-config/`  
**Goal:** Confirm SecMCP covers mcp-guard’s core value for MCP configs and adjacent env files.

## How to reproduce

### Automated (Prompt K acceptance)

From repo root, with both packages editable:

```powershell
pip install -e vendor/mcp-guard
pip install -e "secmcp[dev]"
python -m pytest secmcp/tests/test_parity_mcp_guard.py -v
```

SecMCP-only assertions run without mcp-guard; four tests compare counts to mcp-guard and skip if `mcp_guard` is not installed.

### Manual CLI

```powershell
pip install -e vendor/mcp-guard
pip install -e secmcp

mcp-guard --json "vendor/mcp-guard/examples/unsafe-mcp-config"

python -c "
from secmcp.scanner import check_secrets_sync, scan_vibe_bugs_sync
root = r'vendor/mcp-guard/examples/unsafe-mcp-config'
mcp = root + r'/.cursor/mcp.json'
env = root + '/.env.example'
print('check_secrets', check_secrets_sync(path=env)['count'])
print('scan_vibe_bugs', scan_vibe_bugs_sync(path=mcp)['count'])
"
```

## Finding counts

| Scope | mcp-guard | SecMCP (`check_secrets` + `scan_vibe_bugs`) |
|-------|-----------|-----------------------------------------------|
| `.cursor/mcp.json` only | 2 | 3 (0 secrets + 3 vibe) |
| `.env.example` only | 4 | 4 (`check_secrets`) |
| Whole `unsafe-mcp-config/` | 6 | 7 (4 secrets + 3 vibe) — **automated:** `pytest secmcp/tests/test_scan_repository.py` |

All secret values below are **masked**; fixtures use fake keys only.

### `.cursor/mcp.json`

| Tool | Count | Notes |
|------|-------|-------|
| mcp-guard | 2 | Typed regex: Firecrawl API key (line 7), Qdrant API key (line 14) |
| SecMCP `scan_vibe_bugs` | 3 | Two **literal secret in MCP config** (critical) + **unpinned npx** (medium) |
| SecMCP `check_secrets` | 0 | Expected: env literals are handled by MCP structure scan, not YAML regex on JSON quotes |

**SecMCP-only on this file:** unpinned `npx` / `-y` usage (hygiene from `mcp_config.py`, aligned with mcp-security-audit skill).

### `.env.example`

| mcp-guard kind | Line | SecMCP rule |
|----------------|------|-------------|
| OpenAI API key | 1 | `openai_api_key` |
| Anthropic API key | 2 | `anthropic_api_key` |
| Postgres URL | 3 | `postgres_url_in_source` |
| Generic secret assignment | 4 | `generic_secret_assignment` |

After aligning OpenAI/Anthropic patterns and adding generic + Qdrant YAML rules (MIT mcp-guard attribution), **counts match 4:4** on this file.

## Gaps (intentional or deferred)

| Gap | Owner | Notes |
|-----|-------|-------|
| SARIF export | mcp-guard / Phase 2 | SecMCP has no SARIF yet (`VENDOR_STATUS` item 4) |
| Repo walk + skip dirs | mcp-guard CLI | ✅ `scan_repository_sync` + `secmcp/tests/test_scan_repository.py` |
| `.mcpguardignore` | mcp-guard CLI | Ported in `repo_walk.py` (L7); inline allow comments still vendor-only |
| `--staged` pre-commit | mcp-guard | Not in SecMCP MVP |
| Inline `# mcp-guard:allow` comments | mcp-guard | Not ported |
| Typed `kind` in JSON output | mcp-guard | SecMCP uses `rule` + `message` / MCP-specific text |
| Severity labels | both | mcp-guard: `high` for fixture secrets; SecMCP: `critical` for several secret rules (policy difference, not missed detection) |

## False-positive / reporting differences

- **Duplicate rules:** SecMCP previously fired `generic_secret_assignment` on the same lines as `openai_api_key` / `anthropic_api_key`. Fixed via per-line dedupe in `secmcp/secrets.py` (prefer named rules over generic).
- **Fixture catalog:** Broad `EXAMPLE` line markers suppressed vendor parity fixture hits; catalog now uses `exact_literals` plus token-bound markers only (`secmcp/fixture_catalog.py`).
- **MCP JSON:** mcp-guard does not flag unpinned `npx`; SecMCP does — not a false positive for SecMCP.
- **`check_secrets` on `mcp.json`:** Use `scan_vibe_bugs` (or `get_security_score`) for MCP config paths per `AGENT_SKILL_ROUTING.md`.

## Changes made from this parity run

1. `secmcp/rules/default-rules.yaml` — OpenAI/Anthropic patterns aligned with `vendor/mcp-guard/mcp_guard/scanner.py`.
2. `secmcp/rules/mcp-guard-patterns.yaml` — Qdrant + generic assignment patterns.
3. `secmcp/secrets.py` — per-line dedupe for overlapping secret rules.

## Verdict

For the official mcp-guard unsafe fixture, **SecMCP meets or exceeds mcp-guard on MCP config secrets** and adds **npx pinning** checks. **Env-style assignments** parity is **4:4** on `.env.example` after the rule alignment above. Remaining differences are mostly **CLI ergonomics** (SARIF, repo walk, allow comments), not core MCP-config detection.
