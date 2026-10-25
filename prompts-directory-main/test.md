# Test protocol & guardrails

**Rule:** New behavior = **user test session first**, then **implementation session**. No agent skips T1 for non-trivial features.

## Sessions (strict order)

### Session T1 — User writes tests (human only)

1. New chat/session — **no implementation**.
2. Copy [tests/sessions/TEMPLATE.md](./tests/sessions/TEMPLATE.md) → `tests/sessions/TS-YYYYMMDD-short-name.md`.
3. Fill: goal, acceptance criteria, example inputs/outputs, edge cases, **non-goals**.
4. Do **not** edit `secmcp/tests/` yet.

### Session T2 — Log in TEST_LOG (human or agent)

1. Add a row below (ID, session file, status `pending`).
2. Link the `TS-*.md` file.

### Session T3 — Implementation (agent)

1. Read `brain.md` + the linked `TS-*.md`.
2. Context7 + skills + implement in `secmcp/` (or scripts/workflows).
3. Add **pytest** under `secmcp/tests/test_<name>.py` matching TS spec.
4. Run `cd secmcp && pytest -q`.
5. Set TEST_LOG `impl_status` → `done`; update `brain.md`.

### Session T4 — Forward

Pick next leftover from `brain.md` / `IMPLEMENTATION_PLAN.md`.

---

## Dogfooding / autonomous loop (waives T1)

When the user runs **Prompt O** or **Mode A** (`AGENTS.md`, `.cursor/rules/autonomous-loop.mdc`):

- **T1 is waived** only for items in `brain.md` **L\*** leftover table.
- Agent must still add or update **pytest** in `secmcp/tests/` for new behavior.
- Do not waive T1 for user-requested features outside the L\* table.

---

## Guardrails (all implementation sessions)

| # | Guardrail |
|---|-----------|
| G1 | Context7 before library/API code ([CONTEXT7_MCP.md](./CONTEXT7_MCP.md)) |
| G2 | SecMCP `check_secrets` / `scan_vibe_bugs` on changed source files |
| G3 | No full API keys in tests, logs, or docs — use `fc_fake_…` fixtures |
| G4 | User `tests/sessions/*` is spec-only until T3; agent does not rewrite user intent |
| G5 | Parity tests: `test_parity_mcp_guard.py` must pass when mcp-guard installed |
| G6 | Repo scan: `scripts/scan_repository.py` exit 0 on clean tree in CI |
| G7 | Every TEST_LOG `pending` blocks **new** feature work until T3 or user waives in `TS-*.md` |

---

## TEST_LOG

| ID | Session spec | Impl test file | impl_status | Notes |
|----|--------------|----------------|-------------|-------|
| TS-EXAMPLE | [tests/sessions/TS-EXAMPLE-mcp-config.md](./tests/sessions/TS-EXAMPLE-mcp-config.md) | `secmcp/tests/test_parity_mcp_guard.py` | done | Parity baseline (Prompt K) |
| TS-20251025-scan-repository | [tests/sessions/TS-20251025-scan-repository.md](./tests/sessions/TS-20251025-scan-repository.md) | `secmcp/tests/test_scan_repository.py` | done | Prompt J repo walk + YAML rule proof |
| — | *(add next user session)* | — | pending | — |

**Statuses:** `pending` | `in_progress` | `done` | `waived`

---

## Existing automated tests (reference)

| Area | Path | Run |
|------|------|-----|
| Rules loader | `secmcp/secmcp/rules_loader.py` (`__main__`) | `python -m secmcp.rules_loader` |
| Scanner demo | `secmcp/secmcp/scanner.py` | `python -m secmcp.scanner` |
| Parity mcp-guard | `secmcp/tests/test_parity_mcp_guard.py` | `pytest secmcp/tests/test_parity_mcp_guard.py` |
| Repo scan | `secmcp/tests/test_scan_repository.py` | `pytest secmcp/tests/test_scan_repository.py` |
| Fixture catalog | `secmcp/tests/test_fixture_catalog.py` | `pytest secmcp/tests/test_fixture_catalog.py` |
| CI | `.github/workflows/secmcp-ci.yml` | GitHub Actions |

---

## Agent prompt snippet (append to impl prompts)

```
TEST PROTOCOL (test.md):
- If TEST_LOG has pending rows for this feature, implement only those TS-*.md specs.
- If no TS-*.md exists, STOP and ask user to complete Session T1 (test design) unless change is docs-only or one-line fix.
- After impl: pytest in secmcp/tests/, update TEST_LOG + brain.md.
```

See [taskflow.md](./taskflow.md).
