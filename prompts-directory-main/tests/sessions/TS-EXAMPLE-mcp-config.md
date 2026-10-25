# TS-EXAMPLE-mcp-config

**Author:** project (example)  
**Date:** 2025-10-25  
**Feature / leftover ID:** Parity / Prompt K  
**Phase:** 1

## Goal

SecMCP `scan_vibe_bugs` must detect MCP config issues in mcp-guard’s unsafe example at least as well as the documented parity baseline.

## Acceptance criteria

- [ ] Scan `vendor/mcp-guard/examples/unsafe-mcp-config/.cursor/mcp.json` yields ≥ 3 findings
- [ ] At least 2 findings are `critical` (literal env secrets)
- [ ] `pytest secmcp/tests/test_parity_mcp_guard.py` passes

## Test cases

### TC1 — Unsafe MCP fixture

- **Input:** path above
- **Expected:** ≥3 findings; includes `mcp_config_literal_secret` or equivalent

### TC2 — No raw secrets in tool output

- **Input:** any scan
- **Expected:** masked or no full key strings in JSON

## Non-goals

- Full mcp-guard CLI byte-for-byte match

## Sign-off

- [x] Ready for implementation session (T3) — **done** (see `test_parity_mcp_guard.py`)
