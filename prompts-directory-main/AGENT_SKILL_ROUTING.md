# Agent skill + tool routing

Use with installed skills in `../.agents/skills/` ([INSTALLED.md](../.agents/skills/INSTALLED.md)).

**Every task:** Context7 → skill (if applicable) → SecMCP MCP tools → vendor CLI (optional).

```
Context7 (library docs)
    ↓
.agents/skills/<name>  (workflow / GHAS / audit checklists)
    ↓
SecMCP MCP: check_secrets | scan_vibe_bugs | validate_api_key | get_security_score | list_available_rules
    ↓
vendor/ CLI (parity, SARIF, leakferret verify) — optional
```

## By intent

| You need… | Read skill | SecMCP tool(s) | Vendor optional |
|-----------|------------|----------------|-----------------|
| Snippet / file secrets | secmcp | `check_secrets` | `mcp-guard scan <file>` |
| MCP json hygiene | mcp-security-audit, secmcp | `scan_vibe_bugs` on `.cursor/mcp.json` | mcp-guard on same path |
| Shell injection / unpinned npx in MCP | mcp-security-audit | `scan_vibe_bugs` | — |
| Live key valid? | secmcp | `validate_api_key` | leakferret `verify_finding` |
| Overall risk number | secmcp | `get_security_score` | — |
| Rule catalog | secmcp | `list_available_rules` | leakferret resource `secret-types` |
| Enable GH secret scanning + push protection | secret-scanning | — (org settings) | GitHub MCP `run_secret_scanning` |
| PR security review | security-scan | all tools on diff | mcp-guard `--staged` |
| Harden SecMCP server itself | mcp-server-security | self-scan `server.py` | — |
| Docs match code | docs-guard | — | update `VENDOR_STATUS.md` |
| New phase / RFC | technical-design-doc-creator | — | IMPLEMENTATION_PLAN |
| User-input / LLM injection in app | prompt-injection | `scan_vibe_bugs` | — |
| Find more skills | find-skills | — | `npx skills find …` |
| User test spec (T1) | — (human) | — | `tests/sessions/TS-*.md` |
| Implement logged test (T3) | secmcp + routing row | per TS spec | `pytest secmcp/tests/` |

## File-type hints

| Path | Primary tool |
|------|----------------|
| `**/.cursor/mcp.json`, `**/mcp.json` | `scan_vibe_bugs` (+ skill mcp-security-audit) |
| `**/.env`, `**/*.ts`, `**/*.py` | `check_secrets` |
| Before commit | `get_security_score` on staged snippet |
| `vendor/mcp-guard/examples/**` | Test fixtures only — expect findings |

## Prompt index

| Prompt | Skills to load |
|--------|----------------|
| A, I | secmcp, mcp-server-security |
| C | mcp-security-audit, secmcp |
| E | secret-scanning, docs-guard |
| F | technical-design-doc-creator, secmcp |
| J, K, L | secmcp, find-skills, docs-guard |

Full prompts: [AGENT_PROMPTS.md](./AGENT_PROMPTS.md).
