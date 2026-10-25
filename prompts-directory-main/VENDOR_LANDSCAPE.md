# Existing solutions (REA + ecosystem research)

## Method

1. **Web / GitHub recon** — GitHub MCP secret scanning (hosted), open-source MCP secret tools.
2. **Cloned into `vendor/`** — `mcp-guard`, `leakferret` for source-level comparison.
3. **Cursor browser pass** — passive page structure on [mcp-guard](https://github.com/chiragborse1/mcp-guard) (README features: MCP paths, SARIF, GitHub Action).

REA `inspect_web_page` needs a local CDP target; use browser MCP or clone source for deep analysis.

## Candidates

| Solution | Type | Fits SecMCP plan? | Decision |
|----------|------|-------------------|----------|
| **SecMCP** (`../secmcp`) | Python MCP, 5 tools, YAML rules | **Baseline** — your plan | Keep as primary |
| **mcp-guard** | Python CLI, MCP config focus | Phase 1+2 patterns | **Port** MCP JSON + patterns (MIT) |
| **leakferret** | Rust MCP: scan, classify, verify, rewrite, baseline | Strong verify/rewrite | **Reference**; optional `leakferret` subprocess later |
| **GitHub MCP `run_secret_scanning`** | Remote Copilot MCP | Needs GH Secret Protection | **Complement** in docs, not clone |
| **mcp-security-audit** (skill) | Static `.mcp.json` audit | Config hygiene | Already in prompts checklist |

## Gap SecMCP still owns

- Single MCP with **five named tools** + **declarative YAML** (no vendor lock-in)
- **Vibe bugs** (eval, TLS, CORS) + **weighted score**
- **Phase 3** dashboard + **Phase 2** daily issues (mcp-guard Action is PR-oriented, not issue-based)

## Integration status

**Detailed done / next / skills routing:** [VENDOR_STATUS.md](./VENDOR_STATUS.md) and [AGENT_SKILL_ROUTING.md](./AGENT_SKILL_ROUTING.md).

Summary — **done:**

| From mcp-guard | SecMCP module |
|----------------|---------------|
| `MCP_CONFIG_NAMES` / JSON env walk | `secmcp/mcp_config.py` ✅ |
| Extra provider regexes (Postgres, Pinecone, …) | `rules/mcp-guard-patterns.yaml` ✅ |
| Directory scan skip lists | Phase 2 `scan_repository.py` ⏳ |

| From leakferret | SecMCP |
|-----------------|--------|
| `verify_finding` | `validate_api_key` (subset) ✅ |
| `propose_rewrite` | Phase 4 ⏳ |
| `baseline_diff` | Phase 2 CI ⏳ |

## Optional: run upstream side-by-side

```bash
pip install -e vendor/mcp-guard
mcp-guard scan path/to/.cursor/mcp.json
```

```bash
# leakferret requires Rust build — see vendor/leakferret/README.md
leakferret scan /path/to/repo
```
