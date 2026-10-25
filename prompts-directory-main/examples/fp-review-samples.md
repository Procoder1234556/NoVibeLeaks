# L2 — False positive review (three sample trees)

**Date:** 2025-10-25  
**Scanner:** `scan_repository_sync` / `scripts/scan_repository.py`

## Sample repos (in monorepo)

| Tree | Role | Findings (post-L2) | Notes |
|------|------|-------------------|--------|
| `secmcp/` | Product code + tests | 22 (max 25) | Test fixtures intentionally contain fake keys; vibe rules on test snippets |
| `vendor/mcp-guard/` | Upstream MIT scanner | 1 (max 3) | Root `.mcpguardignore` skips unsafe example dir |
| `prompts-directory-main/` | Docs + prompts | 4 (max 5) | Must not flag markdown security checklists as MCP configs |

## Root cause fixed

**`mcp_args_shell_injection` / `mcp_mutable_package_ref` on markdown:** `scan_mcp_config_text` previously ran whenever the substring `mcpServers` appeared anywhere (including docs describing backticks and `$(…)`). Now MCP-specific checks run only for:

- Canonical MCP config paths (`mcp.json`, `.cursor/mcp.json`, …), or
- **Valid JSON** with a root `mcpServers` object.

## Regression

`secmcp/tests/test_fp_review_samples.py` enforces the upper bounds above. Re-run this review when rules change:

```bash
cd secmcp && pytest tests/test_fp_review_samples.py -v
```

## Out of scope

- Scanning `secmcp/tests/` with zero findings (would require `.mcpguardignore` on tests or moving fixtures).
- Cloning external OSS repos (use this monorepo’s three trees as stand-ins per IMPLEMENTATION_PLAN Phase 1.4).
