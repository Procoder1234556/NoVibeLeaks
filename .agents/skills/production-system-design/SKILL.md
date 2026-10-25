---
name: production-system-design
description: Apply Puneet Patwari (Atlassian) system-design series principles to SecMCP — caching, rate limits, fault tolerance, monolith boundaries, idempotent scans. Use when scaling Phase 2 CI, MCP server hardening, or architecture reviews in this repo.
---

# Production system design (SecMCP)

Source compendium: repo root `puneet_patwari_25_days_system_design_llm.txt`.

## How this maps to SecMCP

| Series topic | SecMCP application |
|--------------|-------------------|
| **Caching (5 layers)** | Browser N/A; MCP client may cache tool results — treat scans as fresh. In-process: YAML rules (`get_rules()`), API validation TTL cache (hash-keyed, never raw keys). |
| **Cache invalidation** | Rules: restart MCP / new process for YAML reload. Validation: cache only definitive outcomes (`valid` / `invalid` / `unknown`), not transient errors. |
| **Rate limiting** | Provider 429 → `rate_limited`; bulkhead on parallel `validate_api_key` (`resilience.py`). CI: `--no-fail` for scheduled jobs, not unbounded live checks. |
| **API gateway** | MCP (`server.py`) is the front door: auth is host IDE; tools route to `scanner.py`. Keep tools thin; logic in library. |
| **Queues / backpressure** | Repo scan is synchronous stream (`iter_repo_files`); skip huge binaries (`MAX_FILE_BYTES`). Future: job queue for dashboard history. |
| **Fault tolerance** | httpx timeouts, retries + jitter on transient validation, semaphores (bulkhead). No unbounded retry on 401. |
| **Idempotency** | `check_secrets` / `scan_repository_sync` are deterministic on same bytes + rules version. Safe to re-run CI. |
| **Monolith vs microservices** | **Modular monolith**: `secmcp/` package + `server.py` + `scripts/`. Split only when deployment or team boundaries force it. |
| **DB scaling order** | Phase 3 Supabase: index → cache → read replicas before sharding. Not applicable until history store ships. |
| **Back-of-envelope** | See `secmcp/docs/PRODUCTION_DESIGN.md` — agent loops, not multi-tenant SaaS RPS. |
| **CAP / consistency** | Scans are CP for a single run (one rules snapshot). Live key check is AP with cached eventual view of provider state. |

## Checklist before shipping scale changes

1. Measure the hot path (repo walk vs live validation vs MCP stdio latency).
2. Add backpressure before adding machines (bulkheads, file skips, concurrency caps).
3. Retries only with jitter; distinguish transient vs permanent failures in caches.
4. Document non-goals (no distributed scan coordinator in Phase 2).
5. Revisit caps when provider limits or repo size profiles change (~6 months).

## Pair with

- `secmcp` — tool playbook
- `mcp-server-security` — MCP deployment
- `technical-design-doc-creator` — Phase 3 TDD
- `docs/PRODUCTION_DESIGN.md` — living architecture notes
