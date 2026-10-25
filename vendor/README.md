# Vendor upstream projects

Cloned for research and selective integration into **SecMCP** (see `prompts-directory-main/VENDOR_LANDSCAPE.md`).

| Repo | License | Role in SecMCP plan |
|------|---------|---------------------|
| [chiragborse1/mcp-guard](mcp-guard/) | MIT | MCP config + extra secret patterns → ported into `secmcp/mcp_config.py` |
| [leakferrethq/leakferret](https://github.com/leakferrethq/leakferret) | Apache-2.0 | Upstream reference (not vendored in git — avoids secret-scan false positives) |

Do not commit real secrets from `mcp-guard/examples/unsafe-mcp-config/`.

Update mcp-guard: `git -C vendor/mcp-guard pull`
