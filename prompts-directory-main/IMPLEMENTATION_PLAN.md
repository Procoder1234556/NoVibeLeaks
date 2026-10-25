# Implementation Plan — SecMCP

**MVP approach:** Phase 1 first; reuse `secmcp` package for 2 and 3.

---

## Phase 1: MCP Server + YAML Rules ✅ (repo: `../secmcp`)

### Step 1.1 — Project skeleton ✅

- [x] `server.py`, `pyproject.toml`, `secmcp/*.py`, `rules/default-rules.yaml`
- [x] Self-check: `python -m secmcp.rules_loader`, `python -m secmcp.scanner`

### Step 1.2 — Five MCP tools ✅

- [x] `check_secrets`, `validate_api_key`, `scan_vibe_bugs`, `get_security_score`, `list_available_rules`
- [x] Smoke in MCP Inspector: `uv run mcp dev server.py` (see `secmcp/README.md`)
- [x] Cursor config on real workspace (`.cursor/mcp.json.example`)

### Step 1.3 — Prompts directory ✅

- [x] Fill `prompts-directory-main/` canonical docs + SKILLS_SETUP
- [x] Install skills → `.agents/skills/` (see INSTALLED.md)
- [x] Vendor clones + VENDOR_STATUS, AGENT_SKILL_ROUTING, prompts J–L

### Step 1.3b — Vendor port (partial) ✅

- [x] `vendor/mcp-guard`, `vendor/leakferret` cloned
- [x] `secmcp/mcp_config.py`, `rules/mcp-guard-patterns.yaml`
- [x] Parity doc (`Prompt K` → `examples/parity-mcp-guard.md`)
- [x] leakferret adapter RFC (`Prompt L` → `rfc/leakferret-adapter.md` + stub)

### Step 1.4 — Hardening

- [x] Review false positives on 3 sample repos (`examples/fp-review-samples.md`, L2)
- [x] Document `validate_keys` cost on large files (`secmcp/README.md`)
- [ ] Optional: reload rules without restart (defer — YAGNI)

**Success:** Agent gets findings &lt; 8s on typical snippet.

**Refs:** PRD P0, TECH_STACK §2, APP_FLOW Flow 1.

---

## Phase 2: GitHub Action (weeks 5–6)

### Step 2.1 — `scripts/scan_repository.py` ✅ (MVP)

- [x] Walk repo via `secmcp.repo_walk` + `scan_repository_sync` (mcp-guard `SKIP_DIRS`)
- [x] Skip binary extensions + 2MB cap
- [x] Exit code non-zero on critical/high findings
- [x] `.mcpguardignore` parity (L7 — `repo_walk.load_ignore_patterns`)

### Step 2.2 — `.github/workflows/secmcp.yml` ✅

```yaml
on:
  schedule: [{ cron: "0 6 * * *" }]
  workflow_dispatch:
```

- [x] `permissions: issues: write`
- [x] Single job: setup Python → install secmcp → run script → `gh issue`

### Step 2.3 — Issue template ✅

Title: `[SecMCP] Daily scan — N findings`  
Body: severity table, file:line, recommendation, link to docs.

- [x] `secmcp/reporting.py` + `scripts/render_daily_issue.py`
- [x] Example: `prompts-directory-main/examples/github-issue-sample.md`

**Success:** One YAML file copy → issues appear next day.

---

## Phase 3: Website (weeks 7–9)

### Step 3.1 — Scaffold ✅

```bash
npx create-next-app@15 secmcp-web --typescript --tailwind --app
```

- [x] `secmcp-web/` Next 15 + Tailwind 4 (`README.md`, `.env.example`)

### Step 3.2 — Supabase (partial)

- [x] `scans` table + RLS migration (`secmcp-web/supabase/migrations/`)
- [x] Anonymous auth client bootstrap for history
- [x] Email/OAuth sign-in UI (`UserMenu` + `/auth/callback`); CI builds web without live Supabase secrets

### Step 3.3 — Scan API ✅

- [x] POST `/api/scan` → subprocess `scripts/scan_snippet.py` (scores only in DB)
- [x] GET `/api/scans` history
- [x] `secmcp/web_payload.py` sanitization + pytest

### Step 3.4 — UI per FRONTEND_GUIDELINES.md (partial)

- [x] Score hero + breakdown cards + findings table + history list (`ScanDashboard.tsx`)
- [x] Landing/marketing page, `ScoreRing` polish, Playwright smoke (`secmcp-web/e2e/`, `secmcp-web-ci.yml`)

**Success:** Upload → score + history row (requires Supabase + anonymous auth).

---

## Phase 4: Launch (week 10+)

- Polish README, 3-minute install video/GIF
- Public GitHub repo + CONTRIBUTING for YAML rules
- Positioning: “security layer for vibe coding” vs docs-only MCPs
- Community rules PR template (no marketplace yet)

---

## Agent build prompt (current step)

When implementing next task, agent MUST:

1. Read [brain.md](./brain.md), [navigation.md](./navigation.md), [test.md](./test.md) ([taskflow.md](./taskflow.md)).
2. **Context7 MCP** — per [CONTEXT7_MCP.md](./CONTEXT7_MCP.md) (before any code).
3. Read **PRD** section for active phase only.
4. Run SecMCP tools on touched files.
5. Follow **TECH_STACK** versions; no new deps without PRD update.
6. Update **brain.md**, **test.md** TEST_LOG, **IMPLEMENTATION_PLAN** checkboxes when done.

See [AGENT_PROMPTS.md](./AGENT_PROMPTS.md) (Prompts M/N for test vs impl sessions).

---

## Testing matrix

| Layer | Check |
|-------|--------|
| rules_loader | `python -m secmcp.rules_loader` |
| scanner | `python -m secmcp.scanner` |
| Prompt K parity | `pytest secmcp/tests/test_parity_mcp_guard.py` (needs `pip install -e vendor/mcp-guard`) |
| MCP | Inspector manual |
| Action | `act` or test repo dispatch |
| Web | Playwright smoke on upload (Phase 3) |
