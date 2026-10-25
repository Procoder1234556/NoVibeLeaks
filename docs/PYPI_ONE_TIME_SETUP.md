# One-time PyPI setup (no API token in GitHub)

Required before **Publish PyPI** or **Release** workflows can upload `novibeleaks`.

1. Create/login at [pypi.org](https://pypi.org).
2. Open **Account settings → Publishing** (Trusted publishers).
3. **Add a new pending publisher** (or add to project `novibeleaks` after first publish):
   - **PyPI Project Name:** `novibeleaks`
   - **Owner:** `Procoder1234556`
   - **Repository:** `NoVibeLeaks`
   - **Workflow name:** `publish-pypi.yml`
   - **Environment name:** `pypi` (optional but matches our workflow)
4. In GitHub repo **Settings → Environments**, create environment **`pypi`** (if using environment name above).
5. Run workflow: **Actions → Publish PyPI → Run workflow**.

Then publish MCP Registry metadata (local):

```bash
npm install -g mcp-publisher
mcp-publisher login github
mcp-publisher publish ./server.json
```
