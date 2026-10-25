# Agent prompts — SecMCP project

Copy-paste into Cursor / Claude Code.

**Mandatory layers (in order):** [brain.md](./brain.md) + [navigation.md](./navigation.md) → [test.md](./test.md) gate → [CONTEXT7_MCP.md](./CONTEXT7_MCP.md) → [.agents/skills/](../.agents/skills/INSTALLED.md) → SecMCP MCP → optional `vendor/` CLI. Session rules: [taskflow.md](./taskflow.md).

**Vendor truth source:** [VENDOR_STATUS.md](./VENDOR_STATUS.md) (what is ported from `vendor/mcp-guard` and `vendor/leakferret` vs still TODO).

---

## Universal Context7 prefix (required)

Prepend this to **every** prompt block below:

```
CONTEXT7 (MANDATORY — before repo read or code):
1. MCP: resolve-library-id → query-docs for the libraries listed in "Context7 for this prompt".
2. Max 3 query-docs calls per turn; one concept per call; never include secrets in queries.
3. If Context7 MCP is missing, stop and ask user to enable it — do not guess library APIs.

Context7 for this prompt: <from section header below each prompt>
```

## Universal agent-skills prefix (required)

Prepend after Context7 block:

```
AGENT SKILLS (this repo — .agents/skills/):
1. Read prompts-directory-main/AGENT_SKILL_ROUTING.md and load the skill(s) listed for this prompt.
2. Apply skill workflows (mcp-security-audit, secret-scanning, docs-guard, etc.) before writing code.
3. Run SecMCP MCP tools on every file you change; never skip scan_vibe_bugs on mcp.json.
4. If porting from vendor/, update VENDOR_STATUS.md when done (docs-guard checklist).
5. TEST PROTOCOL: see test.md — no feature impl without TS-*.md + TEST_LOG row unless user waived.
6. End session: update brain.md (leftovers + recent touched) per taskflow.md.
```

---

## Prompt M — User test design only (T1)

**Skills:** none required (human session) | **Agent:** do not run this as impl.

```
SESSION TYPE: T1 — USER TEST ONLY

You are helping the user AUTHOR tests, not implement code.

Read: test.md, tests/sessions/TEMPLATE.md, brain.md (pick leftover ID).

Output: complete tests/sessions/TS-YYYYMMDD-<name>.md content for user to save.
Add draft TEST_LOG row for test.md (impl_status: pending).

Do NOT edit secmcp/, scripts/, or .github/workflows/.
```

---

## Prompt N — Implement from logged test (T3)

**Skills:** per AGENT_SKILL_ROUTING for the feature | **Context7:** per library touched.

```
[Paste Universal Context7 prefix + agent-skills prefix]

SESSION TYPE: T3 — IMPLEMENTATION

1. Read test.md TEST_LOG and linked tests/sessions/TS-*.md (all acceptance criteria).
2. Read brain.md — only work matching this TS scope.
3. Implement + secmcp/tests/test_*.py
4. pytest -q in secmcp/
5. TEST_LOG → done; brain.md recent touched + leftover ✅ if applicable
```

---

## Prompt O — Autonomous loop (Mode A, Lovable-style local)

**Skills:** `secmcp`, `docs-guard` | **Context7:** only if touching new libraries.

**Use when:** User says “run the loop”, “implement until done”, or references repo root `AGENTS.md`.

```
[Paste Universal Context7 prefix + agent-skills prefix]

SESSION TYPE: T2 — AUTONOMOUS LOOP (Mode A)

Read repo root AGENTS.md and .cursor/rules/autonomous-loop.mdc.

1. brain.md → first ⏳ leftover; IMPLEMENTATION_PLAN scope only.
2. Dogfooding: waive T1 for brain L* items; still add pytest for new behavior.
3. Implement → cd secmcp && pytest -q → scan_repository.py --no-fail . if needed.
4. Update brain.md + IMPLEMENTATION_PLAN + VENDOR_STATUS when applicable.
5. If another ⏳ remains and tests pass, CONTINUE in this session (no “what next?”).
Stop: all L* ✅, pytest blocked twice, or user stop.

Out of scope unless user asks: L6 Phase 3 web scaffold.
```

---

## Prompt A — Implement next phase only

**Skills:** `secmcp`, `mcp-server-security` | **Routing:** [AGENT_SKILL_ROUTING.md](./AGENT_SKILL_ROUTING.md)

**Context7 for this prompt:** `/modelcontextprotocol/python-sdk` — FastMCP tools, ToolError, stdio `run()`; `/encode/httpx` if touching `api_keys.py`.

```
[Paste Universal Context7 prefix — Context7 line above]

You are a senior full-stack + security engineer on SecMCP (VibeSec MCP).

[Paste Universal agent-skills prefix — skills line above]

Read these files in order (do not skip):
1. prompts-directory-main/PRD.md — scope for current phase only
2. prompts-directory-main/IMPLEMENTATION_PLAN.md — next unchecked step
3. prompts-directory-main/VENDOR_STATUS.md — do not re-port what is already ✅
4. prompts-directory-main/TECH_STACK.md — locked stack
5. prompts-directory-main/BACKEND_STRUCTURE.md — module boundaries
6. prompts-directory-main/CONTEXT7_MCP.md — confirm lookups done

Code lives in ../secmcp/. Rules are declarative YAML only — no code execution from rules.
Never log or return full API keys. Tool calls must finish < 8s on typical snippets.

Deliver:
- Minimal diff for the next IMPLEMENTATION_PLAN checkbox
- Run python -m secmcp.scanner self-check
- Update IMPLEMENTATION_PLAN checkboxes you complete
- One line in reply: which Context7 libraryIds you used

Out of scope unless PRD says so: marketplace, freemium billing, arbitrary YAML code execution.
```

---

## Prompt B — Regenerate / refresh PRD from brief

**Context7 for this prompt:** Optional `/websites/model-context-protocol_mintlify_app` — accurate MCP terminology only (product doc, not code).

```
[Paste Universal Context7 prefix — Context7 line above]

Using prompts-directory-main/documentation guide.md Document 1 structure, rewrite PRD.md for SecMCP.

Inputs:
- Product: security MCP for vibe-coded apps (secrets, API key validation, LLM anti-patterns)
- Phases: 1 MCP+YAML, 2 GitHub Action, 3 Next.js+Supabase dashboard, 4 launch
- Constraints: <8s scans, <3min install, masked keys, severity Critical/High/Medium/Low

Keep explicit OUT OF SCOPE. Use SMART success metrics for Phase 1 done-when.
Do not invent features absent from the brief.
If Context7 used, cite MCP terms from query-docs in glossary footnote only.
```

---

## Prompt C — MCP config security pass

**Skills:** `mcp-security-audit`, `secmcp`

**Context7 for this prompt:** `/modelcontextprotocol/python-sdk` — stdio server launch patterns; `/websites/github_en_actions` if workflow configs included.

```
[Paste Universal Context7 prefix — Context7 line above]

Apply the mcp-security-audit skill workflow to this project's MCP configuration.

Read:
- prompts-directory-main/skills/MCP_SECURITY_CHECKLIST.md
- prompts-directory-main/CONTEXT7_MCP.md
- Any .cursor/mcp.json, .mcp.json, or Claude MCP config in repo

Checks: hardcoded secrets, shell injection in args, unpinned npx runners, env vs literals.

Align fixed config with Context7 MCP Python SDK recommended stdio invocation.

Then run SecMCP check_secrets on the config file content if SecMCP is installed.

Output: severity-ordered findings + fixed JSON snippet using python/uv launch for ../secmcp/server.py.
Do not execute configured MCP commands; static analysis only.
```

---

## Prompt D — Fill APP_FLOW for new surface

**Context7 for this prompt:** `/websites/model-context-protocol_mintlify_app` — tool call lifecycle, client/server roles.

```
[Paste Universal Context7 prefix — Context7 line above]

Using documentation guide.md Document 2 template, update APP_FLOW.md for SecMCP.

Include flows for:
- Agent snippet scan (Phase 1)
- validate_api_key with provider branches
- Skills CLI install path (find-skills → mcp-security-audit)
- Context7 lookup step before every agent prompt (link CONTEXT7_MCP.md)
- Phase 2 daily GitHub Issue scan
- Phase 3 dashboard upload

Each flow: happy path, error states, edge cases, exit points.
Add one mermaid diagram for agent tool choice.
```

---

## Prompt E — Phase 2 GitHub Action only

**Skills:** `secret-scanning`, `docs-guard`, `secmcp`

**Context7 for this prompt:** `/websites/github_en_actions` — `schedule`, `workflow_dispatch`, `permissions`, `GITHUB_TOKEN`.

```
[Paste Universal Context7 prefix — Context7 line above]

Implement Phase 2 from IMPLEMENTATION_PLAN.md only.

Read VENDOR_STATUS.md: reuse mcp-guard SKIP_DIRS / scan_path ideas in scan_repository.py — do not fork vendor into MCP tools.

Use secret-scanning skill for optional GHAS alignment; primary scanner remains secmcp package.

Deliver:
1. scripts/scan_repository.py using secmcp.scanner (no duplicate regex)
2. .github/workflows/secmcp.yml — schedule + workflow_dispatch, GITHUB_TOKEN safe
3. Example issue body in prompts-directory-main/examples/github-issue-sample.md
4. Note in VENDOR_STATUS.md if SARIF path deferred vs mcp-guard action

Single workflow file. No composite actions unless unavoidable.
```

---

## Prompt F — Phase 3 dashboard slice

**Context7 for this prompt:** `/vercel/next.js/v15.1.11` — App Router Route Handlers; `/supabase/supabase` — RLS; `/supabase/ssr` — Next.js server client.

```
[Paste Universal Context7 prefix — Context7 line above]

Implement one vertical slice of Phase 3 per FRONTEND_GUIDELINES.md + BACKEND_STRUCTURE.md.

Query Context7 for each framework before scaffolding.

- Next.js 15 App Router page: upload text → POST /api/scan → show overall_score + breakdown
- Supabase: scans table with RLS; store scores/json breakdown only, never raw secrets
- Scanner: subprocess to Python secmcp package (shortest path to shared logic)

Skip: marketplace, OAuth GitHub connect (upload only for this slice).
```

---

## Prompt G — Add YAML rule safely

**Context7 for this prompt:** Resolve PyYAML → `query-docs` for `safe_load` and loader error handling (library id from resolve-library-id).

```
[Paste Universal Context7 prefix — Context7 line above]

Add a new high-confidence rule to ../secmcp/rules/default-rules.yaml.

Requirements:
- name, severity, pattern, message, recommendation, category
- No code execution; regex must be high confidence (explain FP risk in PR description)
- Run python -m secmcp.rules_loader && python -m secmcp.scanner
- Update list_available_rules output count in commit message

If pattern is broad, reject and suggest narrowing.
```

---

## Prompt H — Skills-augmented doc refresh

**Skills:** `docs-guard`, `find-skills`

**Context7 for this prompt:** For each dependency in TECH_STACK.md — `resolve-library-id` + one `query-docs` (cap 3 libs per session).

```
[Paste Universal Context7 prefix + agent-skills prefix]

1. Run docs-guard references/checklist on prompts-directory-main/
2. Sync PRD, TECH_STACK, IMPLEMENTATION_PLAN, VENDOR_STATUS with ../secmcp and vendor/ reality
3. Sync .agents/skills/secmcp/SKILL.md with VENDOR_STATUS
4. Update AGENT_SKILL_ROUTING.md if tools or skills changed
5. Ensure every AGENT_PROMPTS section has Context7 line + skills line

Prefer editing existing docs over new files. English, plain tone.
```

---

## Prompt I — Full implementation brief (greenfield agent)

**Context7 for this prompt:** `/modelcontextprotocol/python-sdk` (v2.x if available in resolve results), `/encode/httpx` async client.

```
[Paste Universal Context7 prefix — Context7 line above]

SecMCP / VibeSec MCP — Full Agent Implementation Brief

[Paste entire product brief from project owner]

Begin with Phase 1 only. Project structure:
secmcp/server.py, rules/default-rules.yaml, secmcp/{scanner,secrets,api_keys,vibe_bugs,scoring,rules_loader}.py

Five tools exact names: check_secrets, validate_api_key, scan_vibe_bugs, get_security_score, list_available_rules.

Use Context7 query-docs for FastMCP @tool(), ToolError, stdio — then implement.
Also: httpx async patterns from Context7 for api_keys.py.

Document 3-minute install in README.
Read prompts-directory-main/ PRD, IMPLEMENTATION_PLAN, CONTEXT7_MCP.md.
```

---

## Prompt J — Port next slice from vendor (controlled)

**Skills:** `secmcp`, `docs-guard`, `mcp-security-audit`

**Context7 for this prompt:** `/modelcontextprotocol/python-sdk`; PyYAML if adding rules.

```
[Paste Universal Context7 prefix + agent-skills prefix]

Read prompts-directory-main/VENDOR_STATUS.md section "What to build next".

Pick ONE item not marked done. Implement only in ../secmcp/ (not vendor/ edits).

Rules:
- MIT mcp-guard / Apache leakferret: attribute in VENDOR_STATUS + comment in new code if pattern copied
- No sixth MCP tool unless PRD amended — extend existing five tools or scanner module
- Run: python -m secmcp.scanner && scan_vibe_bugs on vendor/mcp-guard/examples/unsafe-mcp-config/.cursor/mcp.json
- Mark item ✅ in VENDOR_STATUS.md when complete
```

---

## Prompt K — mcp-guard parity check

**Skills:** `secmcp`, `security-scan`

**Context7:** optional — only if installing mcp-guard deps fails, query Python packaging.

```
[Paste Universal Context7 prefix + agent-skills prefix]

Goal: prove SecMCP covers mcp-guard's core value for MCP configs.

1. pip install -e vendor/mcp-guard (or uv pip install -e)
2. mcp-guard scan vendor/mcp-guard/examples/unsafe-mcp-config/.cursor/mcp.json --format json (or default)
3. SecMCP: scan_vibe_bugs + check_secrets on same file via python -c or MCP
4. Write prompts-directory-main/examples/parity-mcp-guard.md: finding counts, gaps, FP differences
5. If gap is high-value and small, implement in secmcp/ and update VENDOR_STATUS.md

Do not commit real secrets. Use masked output only in parity doc.
```

---

## Prompt L — leakferret bridge design (no Rust in core)

**Skills:** `secmcp`, `technical-design-doc-creator`, `find-skills`

**Context7:** `/modelcontextprotocol/python-sdk` — tool design; subprocess patterns in Python if needed.

```
[Paste Universal Context7 prefix + agent-skills prefix]

Read vendor/leakferret/crates/leakferret-mcp/src/methods.rs tool list.

Design (markdown RFC in prompts-directory-main/rfc/leakferret-adapter.md):
- Which leakferret tools map to existing SecMCP five tools vs stay external CLI
- Env var SECMCP_LEAKFERRET_BIN optional adapter for verify + baseline_diff only
- propose_rewrite: agent prompt-only (user approves edits) — not auto-apply in MVP
- Security: raw secrets never logged; subprocess stdin policy

Do NOT implement Rust. Optional: stub secmcp/leakferret_adapter.py with clear NotImplemented until binary present.

Update VENDOR_STATUS.md "leakferret adapter" row.
```

---

## Examples folder

- [examples/github-issue-sample.md](./examples/github-issue-sample.md) — Phase 2 issue template
- `examples/parity-mcp-guard.md` — create via Prompt K
