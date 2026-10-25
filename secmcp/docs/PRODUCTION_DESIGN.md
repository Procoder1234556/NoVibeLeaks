# SecMCP production design notes

Aligned with [Puneet Patwari’s system design series](../../puneet_patwari_25_days_system_design_llm.txt) (Atlassian Principal Engineer). This document is **scope-specific**: a local/CI security MCP, not a multi-region SaaS.

## Back-of-the-envelope (Day 22)

| Assumption | Order of magnitude |
|------------|-------------------|
| MCP interactive scan | 1 snippet or 1 file, &lt; 2 MB, &lt; 500 ms CPU |
| CI repo scan | 500–5k text files after skips; seconds, not hours |
| Live `validate_api_key` | 1–6 HTTP calls per score run; provider rate limits dominate |
| Peak | Agent burst: tens of tool calls/min per developer, not 10k RPS |

Design for **provider rate limits and variable file size**, not horizontal sharding of the scanner.

## Architecture choice (Days 12–13)

**Modular monolith**: `secmcp/` library, `server.py` (MCP), `scripts/scan_repository.py` (CI). One deployment unit keeps partial-failure surface small; extract a service only if dashboard + multi-tenant history requires it (Phase 3).

## MCP as API gateway (Day 6)

| Responsibility | Where |
|----------------|--------|
| Routing | FastMCP tool names → `scanner.py` |
| AuthZ | Host IDE / OS user; no keys in logs |
| Rate control | Validation bulkhead + provider cache |
| Observability | CI JSON + future dashboard |

## Caching (Days 3–4)

1. **Rules** — loaded once per process (`get_rules()`).
2. **API validation** — SHA-256 keyed TTL cache; masks keys in output.
3. **Invalidation** — process restart for YAML; validation cache skips transient statuses.

Do not cache `rate_limited` / `network_error` for the full TTL (retries should get a fair chance).

## Fault tolerance (Day 14)

- **Timeout**: 6s httpx client per validation.
- **Retry**: up to 3 attempts with full jitter on transient outcomes only.
- **Bulkhead**: max 3 concurrent live validations (`secmcp.resilience`).
- **Circuit breaking**: not global yet; provider 429 surfaced as `rate_limited` to the agent.

## Rate limiting (Day 5)

Primary risk is **self-inflicted**: `get_security_score(validate_keys=True)` over many matches. Bulkhead + sequential de-dupe (`seen` set in `security_score_async`) limits duplicate keys.

Scheduled CI should use static secret rules; use `--no-fail` when appropriate.

## Idempotency (Day 23)

`scan_repository_sync` and snippet scans are pure functions of (content, rules version). Re-running CI on the same commit is safe and expected.

## Phase 3 preview (Days 15–19)

When adding Supabase history:

1. Indexes on `(repo_id, scanned_at)`
2. Cache latest score per branch
3. Read replicas before shard
4. Sagas/outbox for webhook side effects — not 2PC across Stripe + DB

## Operations

- Revisit `MAX_FILE_BYTES`, `SKIP_DIRS`, and `MAX_VALIDATION_CONCURRENCY` when repos or providers change.
- Monitor validation `rate_limited` / `network_error` rates in CI logs before scaling runners.
