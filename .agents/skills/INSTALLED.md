# Installed agent skills (this repo)

Installed with `npx skills add … -y` into `.agents/skills/` (Cursor picks these up for this project).

| Skill | Purpose | When to use |
|-------|---------|-------------|
| **find-skills** | Discover more skills | Any new capability search |
| **secret-scanning** | GitHub secret-scanning workflows | CI / pre-commit secret checks |
| **mcp-security-audit** | Audit `.cursor/mcp.json`, shell injection, pins | Before committing MCP config |
| **security-scan** | General security review | PR / broad code review |
| **mcp-server-security** | MCP server hardening | Building or deploying MCP servers |
| **docs-guard** | Keep docs aligned with code | After IMPLEMENTATION_PLAN changes |
| **technical-design-doc-creator** | TDD / RFC structure | New phases or major features |
| **prompt-injection** | LLM / agent prompt-injection patterns | Vibe-coded apps with user input |
| **secmcp** | This repo’s MCP tool playbook | While coding with `../secmcp` |
| **production-system-design** | Atlassian-style scaling principles for this monolith | CI scale, MCP hardening, Phase 3 TDD |

## Refresh

```bash
cd "d:\cybersecurity mcp server"
npx skills update
```

## Search for more

```bash
npx skills find security mcp
npx skills find documentation agent
```

## Pair with

- **brain / taskflow / navigation / test** — `prompts-directory-main/brain.md`, `taskflow.md`, `navigation.md`, `test.md`
- **Context7 MCP** — `prompts-directory-main/CONTEXT7_MCP.md`
- **SecMCP MCP server** — `secmcp/server.py`
- **Routing** — `prompts-directory-main/AGENT_SKILL_ROUTING.md`
- **Vendor done/TODO** — `prompts-directory-main/VENDOR_STATUS.md`
- **Copy-paste prompts** — `prompts-directory-main/AGENT_PROMPTS.md` (Context7 + skills prefixes)
