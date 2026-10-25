# Vendor integration status

What we **cloned**, what we **ported into SecMCP**, and what **remains** on top. Skills live in [../.agents/skills/](../.agents/skills/INSTALLED.md).

## Cloned (`vendor/`)

| Path | License | Purpose |
|------|---------|---------|
| `vendor/mcp-guard/` | MIT | MCP-focused secret scanner CLI + GitHub Action examples |
| `vendor/leakferret/` | Apache-2.0 | Rust MCP: scan → classify → verify → rewrite → baseline |

## Already in SecMCP (ported / inspired)

| Capability | SecMCP location | Upstream source |
|------------|-----------------|-----------------|
| MCP config file detection | `secmcp/mcp_config.py` | mcp-guard `MCP_CONFIG_NAMES`, suffixes |
| MCP checks scoped to real configs (not docs) | `mcp_config._is_mcp_config_document` | L2 FP review — avoids markdown `mcpServers` prose |
| Literal secrets in MCP `env` JSON | `scan_vibe_bugs` → `scan_mcp_config_text` | mcp-guard `_scan_mcp_json` |
| Shell-ish patterns in MCP args | `mcp_config.py` `_DANGEROUS_ARG_PATTERNS` | awesome-copilot **mcp-security-audit** skill + mcp-guard |
| Unpinned `npx` / `@latest` | `mcp_config.py` | mcp-security-audit skill |
| Postgres / Pinecone / Firecrawl / Qdrant / generic assignment | `rules/mcp-guard-patterns.yaml` | mcp-guard `SECRET_PATTERNS` |
| OpenAI / Anthropic key shapes (incl. `sk-proj-`, short `sk-ant-`) | `rules/default-rules.yaml` | mcp-guard `SECRET_PATTERNS` (Prompt K parity) |
| Per-line secret dedupe (generic vs named) | `secmcp/secrets.py` | mcp-guard span dedupe |
| Default secret + vibe YAML rules | `rules/default-rules.yaml` | Original brief + high-confidence regex |
| API key live check (subset) | `secmcp/api_keys.py` | Plan providers; leakferret has ~25 verifiers |
| Weighted score | `secmcp/scoring.py` | SecMCP plan (not in mcp-guard) |
| Five MCP tools | `server.py` | SecMCP plan |
| Repo walk + skip dirs | `secmcp/repo_walk.py`, `scripts/scan_repository.py` | mcp-guard `SKIP_DIRS` / `scan_path` (Prompt J) |
| `.mcpguardignore` path patterns | `secmcp/repo_walk.py` (`load_ignore_patterns`, `is_ignored_path`) | mcp-guard `IGNORE_FILE_NAME` (L7) |
| Fixture literal allowlist | `secmcp/fixture_catalog.yaml`, `fixture_catalog.py` | leakferret catalog idea (YAML only; Prompt J) |
| Parity regression tests | `secmcp/tests/test_parity_mcp_guard.py` | Prompt K baseline in `examples/parity-mcp-guard.md` |

**Regression check:** `vendor/mcp-guard/examples/unsafe-mcp-config/.cursor/mcp.json` → `scan_vibe_bugs` should report ≥3 findings (env literals + unpinned npx).

## Not ported (use vendor or skills instead)

| Feature | Where it exists | Use when |
|---------|-----------------|----------|
| Full repo walk + skip dirs | mcp-guard `scan_path` | Use `scripts/scan_repository.py` + `repo_walk.py` ✅ |
| SARIF output | mcp-guard `sarif.py` | GitHub Code Scanning upload (Phase 2 alt) |
| Inline allow comments (`mcp-guard: allow`) | mcp-guard | Not ported — use `.mcpguardignore` or fixture catalog |
| Staged-git-only scan | mcp-guard `--staged` | pre-commit hook |
| PyPI package `mcp-secrets-guard` | mcp-guard | `pip install -e vendor/mcp-guard` side-by-side |
| Classify REAL/FIXTURE/UNKNOWN | leakferret MCP | LLM-assisted classification in host |
| In-place rewrite + `.env.example` | leakferret `propose_rewrite` | Phase 4 agent-assisted fix |
| Baseline HMAC diff (new leaks only) | leakferret `baseline_diff` | Phase 2 CI noise reduction |
| 60+ secret types + catalog | leakferret core | Optional subprocess adapter |
| GitHub remote `run_secret_scanning` | GitHub Copilot MCP | Orgs with Secret Protection |

## Recommended stack per task

See [AGENT_SKILL_ROUTING.md](./AGENT_SKILL_ROUTING.md).

## What to build next (priority)

1. **Phase 2** — ✅ `scripts/scan_repository.py`, `scan_repository_sync`, `.github/workflows/secmcp.yml`, issue renderer (`secmcp/reporting.py`).
2. **Parity tests** — ✅ [examples/parity-mcp-guard.md](./examples/parity-mcp-guard.md) + `secmcp/tests/test_parity_mcp_guard.py` (CI: `.github/workflows/secmcp-ci.yml`); re-run when rules change.
3. **leakferret adapter** (optional) — RFC ✅ `rfc/leakferret-adapter.md`; stub `secmcp/leakferret_adapter.py`; subprocess bridge TODO.
4. **SARIF export** — ✅ `build_sarif_from_scan` in `reporting.py`; `scripts/scan_repository.py --sarif PATH`.
5. **Fixture catalog** — ✅ starter `secmcp/fixture_catalog.yaml` (expand from leakferret snapshot as needed).
6. **Rewrite helper** (P4) — new MCP tool or agent prompt only; no auto-commit without user approval.

## Agent skills (`.agents/skills/`)

Installed skills complement vendor code — they do **not** replace SecMCP MCP tools:

| Skill | Overlaps vendor | SecMCP still owns |
|-------|-----------------|-------------------|
| mcp-security-audit | mcp-guard config hygiene | `scan_vibe_bugs` on config paths |
| secret-scanning | GHAS org setup | In-IDE `check_secrets` |
| security-scan | general review | YAML rules + score |
| mcp-server-security | deploying MCP servers | `server.py` hardening |
| secmcp | playbook | All five tools |

## Licenses / attribution

- mcp-guard MIT — patterns in `mcp_config.py` / `mcp-guard-patterns.yaml`; keep `vendor/mcp-guard/LICENSE` in repo.
- leakferret Apache-2.0 — reference only unless you ship a binary adapter; document in README.
