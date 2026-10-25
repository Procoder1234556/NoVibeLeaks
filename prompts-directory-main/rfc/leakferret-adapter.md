# RFC: Optional leakferret binary adapter (L4)

**Status:** Accepted (stub in `secmcp/secmcp/leakferret_adapter.py`)  
**Scope:** Verify + baseline only; no Rust in SecMCP core.

## Problem

SecMCP owns in-IDE scanning with five MCP tools. [leakferret](https://github.com/) (Apache-2.0, `vendor/leakferret/`) adds **live verify**, **baseline diff**, **classify**, and **rewrite** via a separate Rust MCP server. We want optional delegation without merging codebases.

## Tool mapping

| leakferret MCP tool | SecMCP equivalent | Adapter? |
|---------------------|-------------------|----------|
| `scan_repository` | `check_secrets` + `scan_repository_sync` | **No** — SecMCP primary |
| `classify_candidates` | Fixture catalog + YAML rules | **No** — host model / catalog only |
| `propose_rewrite` | — | **No** — agent prompt + user approval only |
| `verify_finding` | `validate_api_key` (subset) | **Yes** — optional when binary present |
| `baseline_diff` | — | **Yes** — optional CI noise reduction |

## Configuration

- `SECMCP_LEAKFERRET_BIN`: absolute path to `leakferret-mcp` (or wrapper) executable.
- If unset or missing: adapter returns `{"available": false, "error": "..."}`; SecMCP behavior unchanged.

## Subprocess policy

- **Stdin:** JSON-RPC only; never pass raw secret strings on argv (Windows length + shell exposure).
- **Stdout/stderr:** Parse JSON; log only rule ids, paths, verdict enums — never `secret` / `value` fields from leakferret payloads.
- **Timeout:** 30s default per call; kill process on overrun.
- **Trust:** Binary is user-supplied; document supply-chain risk in README.

## API surface (Python)

```python
leakferret_available() -> bool
verify_finding_via_leakferret(finding: dict) -> dict  # structured, no raw key echo
baseline_diff_via_leakferret(repo_root: Path) -> dict
```

Future: wire from `validate_api_key` when provider unknown to SecMCP but known to leakferret verifiers (explicit opt-in env `SECMCP_LEAKFERRET_VERIFY=1`).

## Non-goals (MVP)

- Bundling leakferret binary in PyPI wheel.
- Auto `propose_rewrite` commits.
- Replacing SecMCP YAML rules with leakferret regex catalog.

## Rollout

1. Stub adapter + this RFC ✅  
2. Integration tests with mocked subprocess (no real binary in CI).  
3. Document in `secmcp/README.md` + `VENDOR_STATUS.md`.
