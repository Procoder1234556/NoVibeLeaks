# Product Requirements Document: SecMCP (VibeSec MCP) MVP

## Executive Summary

**Product:** SecMCP (working name; alt. VibeSec MCP)  
**Version:** MVP 1.0 (Phase 1 shipped in repo)  
**Document Status:** Final for Phase 1; Draft for Phases 2–3  
**Last Updated:** 2025-10-25  

### Product Vision

Default **security MCP** for AI-assisted development: one server (or one YAML rules file) gives agents **real-time** and **automated** checks for vibe-coding failures—hardcoded secrets, bad API keys, and LLM anti-patterns—with plain-English findings and severity.

### Success Criteria

| Phase | Done when |
|-------|-----------|
| 1 | Agent calls all 5 MCP tools; actionable results in **&lt; 8s** typical project |
| 2 | User adds **one** GitHub workflow; daily issues for findings |
| 3 | User uploads code on web UI; multi-parameter score + history |
| Install | New dev configures MCP in **&lt; 3 minutes** |

---

## Problem Statement

### Problem Definition

Developers using Cursor/Claude/Codex ship code fast but routinely leak **API keys**, ship **invalid credentials**, and copy **unsafe patterns** (disabled TLS, `eval`, open CORS). Generic linters miss provider-specific secrets; security tools are not MCP-native for in-loop agent use.

### Impact Analysis

- **User Impact:** Credential leaks, account compromise, failed prod deploys.
- **Market Impact:** Every AI IDE user is a potential customer; no dominant “security Context7” for vibe coding yet.
- **Business Impact:** Open-source core + optional hosted dashboard/rules later.

---

## Target Audience

### Primary Persona: Vibe Coder (Indie / Startup Dev)

- **Demographics:** 22–40, global, builds with AI daily.
- **Pain Points:** Doesn’t run SAST; forgets `.env`; trusts generated auth/CORS code.
- **Jobs to Be Done:** Ship MVP fast **without** leaking keys or obvious vulns.

### Secondary Persona: Platform / Security Engineer

- Wants **declarative rules**, CI integration, audit trail—not another GUI-only scanner.

| Current Solution | Pain Points | SecMCP Advantage |
|------------------|-------------|-------------------|
| Manual grep | Misses patterns | YAML + curated regex + MCP tools |
| GitHub secret scanning | Post-push only | **In-editor** via MCP |
| Generic SAST | Heavy, slow | &lt; 8s, agent-shaped JSON |

---

## User Stories

### Epic: In-loop security while coding

**Story:** As a **developer using Cursor**, I want the agent to **call security tools on my snippet**, so that **I fix issues before commit**.

**Acceptance Criteria:**

- [ ] `check_secrets`, `validate_api_key`, `scan_vibe_bugs`, `get_security_score`, `list_available_rules` exist
- [ ] Findings include severity, message, location, recommendation
- [ ] Full API keys never returned in tool output

### Epic: Declarative rules

**Story:** As a **security engineer**, I want **YAML rules** without code execution, so that **I can extend detection safely**.

**AC:** Multiple YAML files load; invalid YAML fails gracefully with warnings.

### Epic: CI guardrails (Phase 2)

**Story:** As a **repo owner**, I want **daily scans** that open GitHub Issues, so that **drift is visible**.

### Epic: Human dashboard (Phase 3)

**Story:** As a **team lead**, I want **upload + score history**, so that **I can track risk over time**.

---

## Functional Requirements

### P0 — MCP Server + YAML Rules (Phase 1) ✅

| Feature | Description | AC |
|---------|-------------|-----|
| MCP tools (5) | Exact names per spec | Inspector + Cursor stdio |
| `default-rules.yaml` | High-confidence patterns | OpenAI, AWS, GitHub, Stripe, Anthropic, etc. |
| API key validation | OpenAI, Anthropic, Stripe, Supabase*, GitHub, AWS* | valid / invalid / rate_limited / network_error |
| Scoring | Secrets, API Keys, Configuration, Code Quality, Overall | 0–100 weighted |
| Shared `secmcp/` package | Reused by Action + web later | Importable scanner |

\* Supabase needs `supabase_url`; AWS needs `aws_secret` with access key id.

### P1 — GitHub Action (Phase 2)

- Scheduled + `workflow_dispatch`
- Same scanner as MCP
- Issues/comments via `GITHUB_TOKEN`
- Single workflow file

### P1 — Website / Dashboard (Phase 3)

- Next.js 15 + Supabase
- Upload / GitHub connect, scan, history
- Same scoring dimensions

### P2 — Rule Marketplace

- Community rules; **not** MVP

### Out of Scope (Won't Have in MVP)

- Arbitrary code execution from YAML rules
- Storing user code/keys beyond scan lifetime
- Paid premium rules at launch (recommend no)
- Full SAST / dependency CVE database

---

## Non-Functional Requirements

### Performance

- Typical tool call **&lt; 8 seconds** on snippet/single file
- API validation: short TTL cache (~2 min), respectful rate limits

### Security

- Never log or return full API keys (masked only)
- Rules: declarative regex/messages only
- MCP config: follow [skills/MCP_SECURITY_CHECKLIST.md](./skills/MCP_SECURITY_CHECKLIST.md)

### Usability

- Plain English findings: Critical / High / Medium / Low
- Install path documented in `../secmcp/README.md`

---

## Quality Standards (Anti-Vibe Rules)

- **No** arbitrary `eval` in product code paths handling user rules
- **High-confidence** regex only in default rules (FP kills adoption)
- **ToolError** for recoverable agent failures (missing path, empty input)
- Phase 1: module self-checks (`python -m secmcp.scanner`) not full test pyramid

---

## Success Metrics

### North Star

**Weekly active repos** with SecMCP MCP enabled OR daily Action runs.

### OKRs (first 90 days post-public launch)

1. **Adoption:** 500 GitHub stars OR 1K MCP config copies (tracked via docs analytics)
2. **Quality:** &lt; 5% false-positive reports on default rules
3. **Speed:** p95 tool latency &lt; 8s on 50-line snippet

---

## Constraints & Assumptions

### Constraints

- Python MCP SDK (FastMCP / MCPServer), PyYAML, httpx
- Hosting: optional Railway/Fly for MCP; Vercel + Supabase for web

### Assumptions

- Users run agents that support MCP stdio
- Network allowed for `validate_api_key` only when used

### Open Questions

- Final name: SecMCP vs VibeSec
- Open source only vs freemium dashboard
- Priority provider list after launch feedback

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| False positives | Medium | High | Conservative rules; community toggles later |
| Key sent to validator | Low | Critical | Mask output; no persistence; docs |
| Rate limits on validation | Medium | Medium | Cache; clear rate_limited status |
| Unpinned npx MCP deps | Medium | High | Document pinned python/uv launch |

---

## MVP Definition of Done (Phase 1)

- [x] Five MCP tools implemented in `../secmcp/server.py`
- [x] `rules/default-rules.yaml` + loader
- [x] README install &lt; 3 min
- [ ] MCP Inspector sign-off recorded
- [ ] Cursor dogfood on real project
