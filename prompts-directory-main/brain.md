# Brain — living project state

> **Agents:** Read this at **session start**. Update **session end** (impl sessions only).  
> **Users:** Own test sessions; do not let agents edit `tests/sessions/*` except via your prompt.

**Last updated:** 2025-10-25  
**Current phase:** 3 (Web dashboard) ✅ — Phase 4 launch prep  
**Active focus:** L6 complete; optional production Supabase/Vercel wiring by operator

---

## Leftover work (sync with IMPLEMENTATION_PLAN)

| ID | Item | Primary file(s) | Status |
|----|------|-----------------|--------|
| L1 | MCP Inspector + Cursor dogfood | `secmcp/README.md`, `.cursor/mcp.json.example` | ✅ |
| L2 | Hardening: FP review on 3 repos | `mcp_config.py`, `examples/fp-review-samples.md` | ✅ |
| L3 | `secmcp.yml` scheduled workflow + `gh issue` | `.github/workflows/secmcp.yml` | ✅ |
| L4 | leakferret adapter RFC | `prompts-directory-main/rfc/leakferret-adapter.md` + stub | ✅ |
| L5 | SARIF export | `secmcp/reporting.py`, `scripts/scan_repository.py --sarif` | ✅ |
| L6 | Phase 3 Next.js + Supabase | `secmcp-web/`, `scripts/scan_snippet.py` | ✅ |
| L7 | `.mcpguardignore` parity | `secmcp/repo_walk.py`, `scanner.py` | ✅ |

When you finish an item: mark ✅ here, check box in `IMPLEMENTATION_PLAN.md`, and note in `VENDOR_STATUS.md` if vendor-related.

---

## Recently touched (agent log — newest first)

| Date | Session type | Summary | Files |
|------|--------------|---------|-------|
| 2025-10-25 | impl | L6 finish: landing, auth UI, ScoreRing, Playwright + web CI | `secmcp-web/`, `secmcp-web-ci.yml` |
| 2025-10-25 | impl | L6 Phase 3 start: Next scaffold, `/api/scan`, Python subprocess, Supabase SQL | `secmcp-web/`, `web_payload.py`, `scan_snippet.py` |
| 2025-10-25 | impl | L2 FP review: MCP config scope fix + sample tree regression tests | `mcp_config.py`, `test_fp_review_samples.py`, `fp-review-samples.md` |
| 2025-10-25 | impl | Mode A: AGENTS.md, Prompt O, loop rule; L4 RFC + L5 SARIF + L1 example MCP | `AGENTS.md`, `.cursor/`, `rfc/`, `reporting.py` |
| 2025-10-25 | impl | L7 `.mcpguardignore` parity in repo walk + pytest | `secmcp/repo_walk.py`, `secmcp/scanner.py`, `test_scan_repository.py` |
| 2025-10-25 | impl | Prompt J repo-walk pytest + TS-20251025-scan-repository | `secmcp/tests/test_scan_repository.py`, `tests/sessions/` |
| 2025-10-25 | impl | Phase 2.2: `secmcp.yml`, issue renderer, scan scoring in CI | `.github/workflows/secmcp.yml`, `secmcp/reporting.py`, `scripts/` |
| 2025-10-25 | docs | Agent ops: navigation, taskflow, brain, test protocol | `prompts-directory-main/*.md` |
| — | impl | repo walk, parity tests, fixture catalog, CI | `secmcp/`, `scripts/`, `.github/workflows/secmcp-ci.yml` |

*(Append rows; trim to ~15 lines.)*

---

## Decisions (short)

- **Primary scanner:** SecMCP Python package (not vendor CLI in agent loop).
- **Five MCP tools:** no sixth without PRD change.
- **Tests:** user spec session → `tests/sessions/` → log in `test.md` → impl session → pytest in `secmcp/tests/`.

---

## Quick health

```bash
cd secmcp && python -m secmcp.scanner && python -m secmcp.rules_loader
cd secmcp && pytest -q
python scripts/scan_repository.py --help
```

---

## Do not stale

If `brain.md` disagrees with `IMPLEMENTATION_PLAN.md`, **fix brain** after confirming plan is truth for scope.
