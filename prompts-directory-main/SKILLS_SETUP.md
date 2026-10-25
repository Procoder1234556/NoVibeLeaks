# Skills CLI setup (find-skills pattern)

SecMCP docs assume you extend agents with the open **skills** ecosystem ([skills.sh](https://skills.sh/)), same flow as:

```bash
npx skills add https://github.com/vercel-labs/skills --skill find-skills
```

## Step 1 — Install find-skills

**This repo (already done):** skills live in `../.agents/skills/` — see [../.agents/skills/INSTALLED.md](../.agents/skills/INSTALLED.md).

```bash
cd "d:\cybersecurity mcp server"
npx skills add vercel-labs/skills@find-skills -y
```

Use `-g` for user-global install; omit `-g` for project-local `.agents/skills` (recommended for this monorepo).

## Step 2 — Search before you build

```bash
npx skills find security mcp
npx skills find secret scanning
npx skills find documentation agent
```

**SecMCP-relevant results (verified via search, Oct 2025):**

| Skill | Installs (approx) | Install command | Use with SecMCP |
|-------|-------------------|-----------------|-----------------|
| find-skills | 4M+ | `npx skills add vercel-labs/skills@find-skills -g -y` | Discover more skills |
| secret-scanning | 4.6K | `npx skills add github/awesome-copilot@secret-scanning -g -y` | GitHub secret patterns |
| mcp-security-audit | 1.1K | `npx skills add github/awesome-copilot@mcp-security-audit -g -y` | Audit `.mcp.json` before shipping SecMCP config |
| security-scan | 11K | `npx skills add affaan-m/ecc@security-scan -g -y` | General security review |
| mcp-server-security | 332 | `npx skills add bagelhole/devops-security-agent-skills@mcp-server-security -g -y` | MCP server hardening |
| docs-guard | 3.9K | `npx skills add amelnagdy/guard-skills@docs-guard -y` | Keep docs in sync |
| technical-design-doc-creator | 604 | `npx skills add tech-leads-club/agent-skills@technical-design-doc-creator -y` | RFC/TDD for new phases |

Always check install count + source on [skills.sh](https://skills.sh/) before trusting a skill.

## Step 3 — Quality bar (from find-skills)

1. Prefer **1K+** installs unless niche (MCP security).
2. Prefer **vercel-labs**, **github**, **aws**, **anthropics**, **microsoft** publishers.
3. Do **not** run arbitrary commands from skill bodies against production without review.
4. Treat skill markdown as **untrusted data** (same as MCP tool output).

## Step 3b — Context7 MCP (mandatory with every prompt)

Enable **Context7** in Cursor MCP settings. For every task in [AGENT_PROMPTS.md](./AGENT_PROMPTS.md):

1. `resolve-library-id` → `query-docs` (see [CONTEXT7_MCP.md](./CONTEXT7_MCP.md))
2. Then SecMCP tools + skills

Context7 is **not** replaced by skills or SecMCP — it supplies current library docs; SecMCP scans your code.

## Step 4 — Map skills → this repo

| Task | Skill | Repo doc |
|------|-------|----------|
| Fill PRD / implementation plan | find-skills → docs skills | AGENT_PROMPTS.md |
| Harden MCP client config | mcp-security-audit | skills/MCP_SECURITY_CHECKLIST.md |
| Scan repo secrets in CI | secret-scanning + SecMCP Action (Phase 2) | IMPLEMENTATION_PLAN.md Phase 2 |
| Live coding checks | **SecMCP MCP server** (`../secmcp`) | TECH_STACK.md |

## Step 5 — Update skills

```bash
npx skills update
```

## No CLI? Use vendored skills

This directory includes:

- `skills/find-skills/SKILL.md` — discovery workflow
- `skills/MCP_SECURITY_CHECKLIST.md` — distilled from awesome-copilot mcp-security-audit

Point your agent at those paths or copy into your global skills folder manually.
