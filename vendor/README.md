# Vendor upstream projects

Cloned for research and selective integration into **SecMCP** (see `prompts-directory-main/VENDOR_LANDSCAPE.md`).

| Repo | License | Role in SecMCP plan |
|------|---------|---------------------|
| [chiragborse1/mcp-guard](mcp-guard/) | MIT | MCP config + extra secret patterns → ported into `secmcp/mcp_config.py` |
| [leakferrethq/leakferret](leakferret/) | Apache-2.0 | Reference for verify/rewrite/baseline; optional sidecar later (Rust binary) |

Do not commit real secrets from `mcp-guard/examples/unsafe-mcp-config/`.

Update clones: `git -C vendor/mcp-guard pull` / `git -C vendor/leakferret pull`
