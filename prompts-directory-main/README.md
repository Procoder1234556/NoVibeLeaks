# SecMCP / VibeSec — AI-First Prompts Directory

Knowledge base for building **SecMCP**: the default security MCP for vibe-coded apps (Cursor, Claude Code, Codex). Use these docs **before** extending code so agents stay aligned.

## Start here

| Order | Document | Purpose |
|-------|----------|---------|
| ★ | [brain.md](./brain.md) | **Living state** — leftovers, recent changes (update every impl session) |
| ★ | [taskflow.md](./taskflow.md) | Session types T1–T4, doc update duties |
| ★ | [navigation.md](./navigation.md) | Paths, glossary, fast `rg` hints |
| ★ | [test.md](./test.md) | User test session → TEST_LOG → impl → pytest |
| 0 | [CONTEXT7_MCP.md](./CONTEXT7_MCP.md) | **Required** Context7 `resolve-library-id` + `query-docs` on every prompt |
| 0b | [../.agents/skills/INSTALLED.md](../.agents/skills/INSTALLED.md) | Installed agent skills (this repo) |
| 0c | [AGENT_SKILL_ROUTING.md](./AGENT_SKILL_ROUTING.md) | Which skill + SecMCP tool per task |
| 0d | [VENDOR_STATUS.md](./VENDOR_STATUS.md) | What `vendor/` contributed vs still to build |
| 0e | [SKILLS_SETUP.md](./SKILLS_SETUP.md) | Discover & install more skills (`npx skills`) |
| 1 | [PRD.md](./PRD.md) | What we build, for whom, success criteria |
| 2 | [APP_FLOW.md](./APP_FLOW.md) | MCP, CI, and dashboard user paths |
| 3 | [TECH_STACK.md](./TECH_STACK.md) | Locked versions & install |
| 4 | [FRONTEND_GUIDELINES.md](./FRONTEND_GUIDELINES.md) | Phase 3 dashboard UI |
| 5 | [BACKEND_STRUCTURE.md](./BACKEND_STRUCTURE.md) | Scanner lib, MCP, future API/DB |
| 6 | [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) | Build order (Phase 1 → 4) |
| — | [AGENT_PROMPTS.md](./AGENT_PROMPTS.md) | Copy-paste prompts for each document |
| — | [documentation guide.md](./documentation%20guide.md) | Meta-guide (all 6 doc types + research) |

## Code location

Implementation lives in sibling folder: `../secmcp/` (MCP server + `secmcp/` Python package).

**Existing solutions:** cloned under `../vendor/` — [VENDOR_LANDSCAPE.md](./VENDOR_LANDSCAPE.md) (research), [VENDOR_STATUS.md](./VENDOR_STATUS.md) (ported vs roadmap).

## Skills ecosystem (recommended)

Install on your machine (user approval required in locked-down environments):

```bash
npx skills add vercel-labs/skills@find-skills -g -y
npx skills add github/awesome-copilot@secret-scanning -g -y
npx skills add github/awesome-copilot@mcp-security-audit -g -y
npx skills add affaan-m/ecc@security-scan -g -y
```

Vendored copy of **find-skills**: [skills/find-skills/SKILL.md](./skills/find-skills/SKILL.md).

## Agent workflow

1. Read [brain.md](./brain.md) + [navigation.md](./navigation.md).
2. **Test gate:** [test.md](./test.md) — pending TEST_LOG? implement that `TS-*.md` only; else ask user for T1 session.
3. **Context7 MCP** — [CONTEXT7_MCP.md](./CONTEXT7_MCP.md) (every [AGENT_PROMPTS.md](./AGENT_PROMPTS.md) block).
4. **Agent skill** — [AGENT_SKILL_ROUTING.md](./AGENT_SKILL_ROUTING.md).
5. **PRD** + **IMPLEMENTATION_PLAN** + **VENDOR_STATUS** for phase scope.
6. SecMCP MCP tools on changed files.
7. End: update **brain.md**, **test.md** TEST_LOG, plan checkboxes ([taskflow.md](./taskflow.md)).
