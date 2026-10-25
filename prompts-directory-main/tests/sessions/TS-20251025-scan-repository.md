# TS-20251025-scan-repository

**Goal:** Lock Prompt J repo-walk behavior (`scan_repository_sync` / `scripts/scan_repository.py`) to parity doc counts and mcp-guard skip-dir semantics.

## Acceptance criteria

1. Whole `vendor/mcp-guard/examples/unsafe-mcp-config/` scan yields **7** findings (parity-mcp-guard.md).
2. Result includes Phase 2 score fields: `overall_score`, `grade`, `breakdown`, `summary`.
3. `node_modules` (and other `SKIP_DIRS`) are not scanned; clean file under `src/` still counts as scanned.
4. Binary extensions (e.g. `.png`) are skipped.
5. Every finding `rule` name must exist in the loaded YAML rule catalog (`get_rules()`), proving detection is not hardcoded in `scanner.py`.
6. Injected `github_pat` in a **temp** tree is flagged via rule `github_pat` without placing `GITHUB_TOKEN` in a committed `.env`.
7. Finding payloads must not contain vendor fixture literals (G3).

## Non-goals

- Live `validate_api_key` for GitHub when `GITHUB_TOKEN` is unset (no mock token in `.env`).
- `.mcpguardignore` (L7 optional).
- mcp-guard CLI count comparison (covered by `test_parity_mcp_guard.py`).

## Impl test file

`secmcp/tests/test_scan_repository.py`
