---
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.
---

# Find Skills

Discover and install skills from the open agent skills ecosystem.

## When to Use

- User asks "how do I do X" where a skill may exist
- "find a skill for X" / "is there a skill for X"
- Extending agent capabilities (security, MCP, docs, testing)

## Skills CLI

- `npx skills find [query] [--owner <owner>]`
- `npx skills add <package>` — e.g. `npx skills add vercel-labs/skills@find-skills -g -y`
- `npx skills update`
- Browse: https://skills.sh/

## Workflow

1. Identify domain + task (e.g. SecMCP → `npx skills find security mcp`).
2. Check leaderboard on skills.sh for popular options.
3. Search CLI; verify installs + publisher.
4. Present install command + skills.sh link.
5. Install with user consent: `npx skills add <owner/repo@skill> -g -y`.

## SecMCP defaults

After find-skills, recommend:

```bash
npx skills add github/awesome-copilot@mcp-security-audit -g -y
npx skills add github/awesome-copilot@secret-scanning -g -y
```

Then wire `../secmcp` MCP server per TECH_STACK.md.

## No match?

Help directly; suggest `npx skills init my-skill` for repeated workflows.
