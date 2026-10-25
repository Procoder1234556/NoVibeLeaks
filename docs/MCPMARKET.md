# List NoVibeLeaks on MCPmarket

Two paths: **public directory** (discovery) and **MCP Market HUB** (hosted connect for your org).

## A. Public directory (free, review queue)

1. Open [mcpmarket.com/submit](https://mcpmarket.com/submit).
2. Choose **MCP Server**.
3. Repository URL:

   `https://github.com/Procoder1234556/NoVibeLeaks`

4. Submit — you’ll get email when the listing is live ([submit page](https://mcpmarket.com/submit)).

Ensure the README has install steps (`uvx novibeleaks`) and tool list. Optional paid “Get Listed Now” is on their site.

## B. Your HUB connect link (managed deploy)

Your link: [app.mcpmarket.com/p03490978/connect](https://app.mcpmarket.com/p03490978/connect)

1. **Sign in** with GitHub or Google (required — we cannot authenticate for you).
2. After redirect, use **Custom Deploy** ([docs](https://docs.mcpmarket.com/docs/mcp-servers/deploying-a-custom-mcp-server)):
   - **Tools → Browse MCPs → Custom Deploy**
3. Pick a source (use one):

   | Source | Value |
   |--------|--------|
   | **GitHub** | `https://github.com/Procoder1234556/NoVibeLeaks` (entry: `secmcp/server.py` or package build) |
   | **PyPI** | `novibeleaks` (after [PyPI publish](./PYPI_ONE_TIME_SETUP.md)) |

4. **Name:** `NoVibeLeaks`
5. **Transport:** stdio (Python MCP)
6. Click **Deploy** and wait for Pending → Running.

Private repos need [support@mcpmarket.com](mailto:support@mcpmarket.com).

## Before HUB / PyPI deploy

- [ ] PyPI: run GitHub **Publish PyPI** after [trusted publisher setup](./PYPI_ONE_TIME_SETUP.md)
- [ ] Optional: [official MCP Registry](./MCP_REGISTRY.md) (`server.json`)

## C. MCPmarket link in Cursor (API token)

Use this to use **MCPmarket’s hosted MCP gateway** in Cursor (toolkits from their catalog), separate from listing NoVibeLeaks.

1. In [MCPmarket HUB](https://app.mcpmarket.com) → **API Tokens** → create a token (shown once).
2. Set a **user** environment variable (do not commit the key):

   **Windows (PowerShell, persistent):**

   ```powershell
   [Environment]::SetEnvironmentVariable('MCPMARKET_API_KEY', 'YOUR_KEY', 'User')
   ```

   Restart Cursor so it picks up the variable (apps from the Dock/shell may not see one-off exports).

3. Add to `%USERPROFILE%\.cursor\mcp.json`:

   ```json
   "mcpmarket": {
     "url": "https://link.mcpmarket.com/mcp",
     "headers": {
       "Authorization": "Bearer ${env:MCPMARKET_API_KEY}"
     }
   }
   ```

See [Cursor MCP docs](https://docs.cursor.com/context/mcp).

If a key was pasted into chat or a repo, **revoke it in MCPmarket and create a new token**.

## Copy-paste blurb for forms

**Name:** NoVibeLeaks  
**Tagline:** Stop secret leaks in vibe-coded apps  
**Description:** MCP server with five tools: secrets scan, API key validation, vibe-coding anti-patterns, security score, and YAML rules — for Cursor and Claude Code.
