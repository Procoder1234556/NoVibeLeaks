# Navigation — reach any resource fast

**Repo root:** `d:\cybersecurity mcp server\` (adjust if cloned elsewhere).

## Agent entry (read first)

| Need | Open |
|------|------|
| Autonomous loop (Mode A) | [../AGENTS.md](../AGENTS.md) + Prompt O in [AGENT_PROMPTS.md](./AGENT_PROMPTS.md) |
| What phase + leftovers | [brain.md](./brain.md) |
| Which session type am I in? | [taskflow.md](./taskflow.md) |
| Test guardrails + log | [test.md](./test.md) |
| Copy-paste prompt | [AGENT_PROMPTS.md](./AGENT_PROMPTS.md) |
| Skill + tool pick | [AGENT_SKILL_ROUTING.md](./AGENT_SKILL_ROUTING.md) |

## One-line paths (from repo root)

| Goal | Path |
|------|------|
| MCP server | `secmcp/server.py` |
| Scanner library | `secmcp/secmcp/scanner.py` |
| YAML rules | `secmcp/rules/*.yaml` |
| MCP config logic | `secmcp/secmcp/mcp_config.py` |
| Repo walk / CI scan | `secmcp/secmcp/repo_walk.py`, `scripts/scan_repository.py` |
| Pytest | `secmcp/tests/` |
| User test specs (sessions) | `prompts-directory-main/tests/sessions/` |
| Vendor upstream | `vendor/mcp-guard/`, `vendor/leakferret/` |
| Installed agent skills | `.agents/skills/` |
| CI workflow | `.github/workflows/secmcp-ci.yml` |
| Daily scan | `.github/workflows/secmcp.yml` |
| Parity doc | `prompts-directory-main/examples/parity-mcp-guard.md` |

## Prompts directory map

```
prompts-directory-main/
├── brain.md              ← living state (agents update every session)
├── taskflow.md           ← session order + doc update duties
├── navigation.md         ← this file
├── test.md               ← test protocol + TEST_LOG
├── tests/sessions/       ← user-written test specs (one file per session)
├── README.md             ← doc index
├── AGENT_PROMPTS.md
├── CONTEXT7_MCP.md
├── VENDOR_STATUS.md
├── IMPLEMENTATION_PLAN.md
└── PRD.md … (canonical six + guides)
```

## Resource glossary

| Term | Meaning | Where |
|------|---------|--------|
| **SecMCP** | Python MCP server + library | `secmcp/` |
| **Five tools** | `check_secrets`, `validate_api_key`, `scan_vibe_bugs`, `get_security_score`, `list_available_rules` | `secmcp/server.py` |
| **Context7** | MCP for up-to-date library docs | IDE MCP `user-context7` |
| **Agent skill** | Markdown workflow in `.agents/skills/<name>/` | [INSTALLED.md](../.agents/skills/INSTALLED.md) |
| **Vendor port** | Code copied/adapted from `vendor/` | [VENDOR_STATUS.md](./VENDOR_STATUS.md) |
| **User test session** | Human-only: write acceptance tests, no impl | [tests/sessions/](./tests/sessions/README.md) |
| **TEST_LOG** | Registry in `test.md` linking session → pytest | [test.md](./test.md) |
| **brain.md** | Single-page “what’s left + last change” | Must update after impl sessions |
| **Parity** | SecMCP vs mcp-guard comparison | `examples/parity-mcp-guard.md` |
| **Fixture catalog** | Known-safe example secrets (reduce FP) | `secmcp/secmcp/fixture_catalog.yaml` |
| **REA MCP** | Reverse-engineering / web inspect tools | IDE MCP `user-rea` (optional recon) |

## External resources

| Resource | URL / command |
|----------|----------------|
| Skills catalog | https://skills.sh/ |
| Install skill | `npx skills add <owner/repo@skill> -y` |
| MCP Python SDK docs | Context7 `/modelcontextprotocol/python-sdk` |
| mcp-guard CLI | `pip install -e vendor/mcp-guard` → `mcp-guard scan …` |

## Fast search (agent)

| Looking for… | Command / action |
|--------------|------------------|
| Tool definitions | `rg "@mcp.tool" secmcp/server.py` |
| Rule names | `rg "^  - name:" secmcp/rules/` |
| Unchecked plan items | `rg "\[ \]" prompts-directory-main/IMPLEMENTATION_PLAN.md` |
| Leftover vendor work | `rg "⏳\|build next" prompts-directory-main/VENDOR_STATUS.md` |
| Session tests | `ls prompts-directory-main/tests/sessions/*.md` |

## After you change code

Update in order: **test.md** (if tests) → **brain.md** → **IMPLEMENTATION_PLAN** / **VENDOR_STATUS** → **taskflow.md** (only if process changed).

See [taskflow.md](./taskflow.md).
