# Context7 MCP — mandatory for every agent prompt

**Rule:** No SecMCP prompt in [AGENT_PROMPTS.md](./AGENT_PROMPTS.md) may run without **Context7** lookups first. Training data is stale; stack APIs change (MCP SDK, Next.js, Supabase, Actions).

## Enable Context7 in Cursor

1. **Settings → MCP** → add Context7 server (or use built-in `user-context7` if already connected).
2. Confirm tools: `resolve-library-id`, `query-docs`.
3. If auth required: call `mcp_auth` once for the Context7 namespace.

## Required workflow (every task)

```
1. resolve-library-id(libraryName, query)  → pick official / High reputation ID
2. query-docs(libraryId, query, language?) → one concept per call (max 3 calls per user question)
3. Implement using doc facts; cite libraryId in PR/commit notes when non-obvious
4. Never put secrets, API keys, or proprietary code in Context7 queries
```

**Order with other tools:**

| Step | Tool |
|------|------|
| 1 | Context7 (libraries for this task) |
| 2 | SecMCP MCP (`check_secrets`, etc.) on code you write |
| 3 | Skills (`find-skills`, `mcp-security-audit`) per [SKILLS_SETUP.md](./SKILLS_SETUP.md) |

## SecMCP library map (pre-resolved IDs)

Use these IDs directly when the task matches; otherwise run `resolve-library-id` again.

| Task / phase | libraryName | Context7 library ID | Example `query-docs` query |
|--------------|-------------|---------------------|----------------------------|
| MCP server, FastMCP, tools | Model Context Protocol Python SDK | `/modelcontextprotocol/python-sdk` | "FastMCP @tool decorator stdio server run" |
| MCP spec concepts | Model Context Protocol | `/websites/model-context-protocol_mintlify_app` | "MCP tools structured output ToolError" |
| Phase 3 web UI | Next.js | `/vercel/next.js` or `/vercel/next.js/v15.1.11` | "App Router Route Handler POST request body" |
| Phase 3 DB/auth | Supabase | `/supabase/supabase` | "Row Level Security policies auth.uid()" |
| Supabase in Next SSR | Supabase SSR | `/supabase/ssr` | "createServerClient Next.js App Router" |
| API key HTTP checks | HTTPX | `/encode/httpx` | "AsyncClient timeout context manager" |
| YAML rules | PyYAML | resolve if needed | "safe_load load yaml file" |
| Phase 2 CI | GitHub Actions | `/websites/github_en_actions` | "workflow schedule cron workflow_dispatch permissions" |
| Open issues from Action | GitHub CLI / REST | `/websites/github_en_actions` | "GITHUB_TOKEN permissions issues write" |

### Version pinning

When [TECH_STACK.md](./TECH_STACK.md) names a version, prefer Context7 ID with version suffix when available (e.g. `/vercel/next.js/v15.1.11`).

## Copy-paste block (prepend to ANY prompt)

Insert at the **top** of every fenced prompt in AGENT_PROMPTS.md:

```text
CONTEXT7 (MANDATORY — do this before reading repo or writing code):
1. Use MCP tools resolve-library-id + query-docs for each library in the "Context7 for this prompt" line below.
2. Max 3 query-docs calls; one topic per call; no secrets in queries.
3. If Context7 unavailable, stop and ask user to enable Context7 MCP — do not guess API shapes.

Context7 for this prompt: <see prompt-specific line>
```

## Prompt-specific Context7 lines

| Prompt | Context7 for this prompt |
|--------|-------------------------|
| A | `/modelcontextprotocol/python-sdk` — tools, ToolError, stdio |
| B | none required (product doc only); optional `/websites/model-context-protocol_mintlify_app` for MCP glossary |
| C | `/modelcontextprotocol/python-sdk` — server config; `/websites/github_en_actions` if CI config touched |
| D | `/websites/model-context-protocol_mintlify_app` — client/server flow |
| E | `/websites/github_en_actions` — schedule, permissions, GITHUB_TOKEN |
| F | `/vercel/next.js/v15.1.11`, `/supabase/supabase`, `/supabase/ssr` |
| G | PyYAML safe_load (resolve library id for PyYAML) |
| H | resolve-library-id for any lib mentioned in synced TECH_STACK |
| I | `/modelcontextprotocol/python-sdk`, `/encode/httpx` |

## Anti-patterns

- Skipping Context7 because "I already know FastMCP"
- One giant query-docs: "Next.js routing auth supabase and MCP"
- Pasting user `.env` or live `sk-…` keys into Context7 queries
- Using Context7 for pure product copy (PRD prose) instead of library facts

## Verification checklist (agent self-check)

- [ ] Called `resolve-library-id` at least once for this task (unless ID from table above)
- [ ] Called `query-docs` before editing code for external libraries
- [ ] Noted which libraryId informed the implementation
- [ ] Ran SecMCP on changed files after code edits
