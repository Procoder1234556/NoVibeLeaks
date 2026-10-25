# Publish NoVibeLeaks to the MCP Registry

The [official MCP Registry](https://registry.modelcontextprotocol.io/) lists public servers for clients and marketplaces (Cursor, Claude, aggregators).

## Prerequisites

1. GitHub repo: `https://github.com/Procoder1234556/NoVibeLeaks`
2. PyPI package **`novibeleaks`** at version matching [`server.json`](../server.json)
3. README contains `<!-- mcp-name: io.github.Procoder1234556/novibeleaks -->` (root + PyPI package readme)

## 1. Publish to PyPI

```bash
cd secmcp
uv build
uv publish   # requires PyPI token or trusted publishing
```

Or use the GitHub Action **Release** workflow after adding `PYPI_API_TOKEN` as a repository secret.

## 2. Install publisher CLI

```bash
npm install -g mcp-publisher
```

## 3. Authenticate (GitHub namespace)

```bash
mcp-publisher login github
```

Your `server.json` name must be `io.github.Procoder1234556/novibeleaks`.

## 4. Publish metadata

From the repository root:

```bash
mcp-publisher publish ./server.json
```

## 5. Verify

Search the registry API or your MCP client’s marketplace after sync (aggregators may cache ~1 hour).

---

**Note:** Registry validation checks that the PyPI package README includes the exact `mcp-name:` line for your server name.
