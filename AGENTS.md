# Agent instructions — SecMCP repo

This file is the **local “Lovable-style” loop** entry: one place for Cursor / Claude Code to run repeated implement → test → update state cycles without re-explaining the project.

## Mode A — Autonomous loop (default when user says “run loop” / Prompt O)

**Stop conditions:** brain.md L* table has no ⏳ items, pytest fails and cannot be fixed in two attempts, or user says stop.

Each iteration:

1. Read `prompts-directory-main/brain.md` → pick the **topmost ⏳** row (L1 before L6).
2. Read `prompts-directory-main/navigation.md` + `IMPLEMENTATION_PLAN.md` for scope.
3. **Dogfooding:** T1 `tests/sessions/*` is **waived** for brain L* items only; still add/update `secmcp/tests/` for new behavior.
4. Implement minimal diff; run `cd secmcp && pytest -q`.
5. Run `python scripts/scan_repository.py --no-fail .` if you touched `secmcp/` or `scripts/`.
6. Update `brain.md` (✅ + recent touched), `IMPLEMENTATION_PLAN.md` checkboxes, `VENDOR_STATUS.md` if vendor-related.
7. If iteration succeeded and another ⏳ remains, **continue** in the same session (do not ask “what next?”).

**Mandatory:** Context7 before new library APIs (`prompts-directory-main/CONTEXT7_MCP.md`). SecMCP MCP tools on changed source when MCP is connected. No full API keys in repo.

**Optional pacing:** In Cursor chat, `/loop 30m` + Prompt O for timed ticks (see `.cursor/skills` loop skill).

## Mode B — Strict test protocol

User-owned features: follow `prompts-directory-main/test.md` (T1 → TEST_LOG → T3). Do not waive T1 unless `test.md` dogfooding section applies.

## Project map

| What | Where |
|------|--------|
| Living backlog | `prompts-directory-main/brain.md` |
| Copy-paste prompts | `prompts-directory-main/AGENT_PROMPTS.md` (Prompt **O** = loop) |
| MCP server | `secmcp/server.py` |
| CI scan | `scripts/scan_repository.py` |

## Health check

```bash
cd secmcp && pytest -q
python scripts/scan_repository.py --no-fail .
```
