# Backend Architecture — SecMCP

Covers Phase 1 Python core, MCP adapter, and Phase 2–3 extensions.

## 1. High-Level Diagram

```
┌─────────────┐     stdio      ┌──────────────┐
│ Cursor /    │ ◄────────────► │ server.py    │
│ Claude MCP  │                │ (FastMCP)    │
└─────────────┘                └──────┬───────┘
                                      │
                              ┌───────▼────────┐
                              │ scanner.py     │
                              │ orchestration  │
                              └───┬───┬───┬────┘
                    ┌─────────────┘   │   └─────────────┐
            ┌───────▼──────┐  ┌─────▼─────┐   ┌───────▼──────┐
            │ secrets.py   │  │ vibe_bugs │   │ api_keys.py  │
            └───────┬──────┘  └─────┬─────┘   └───────┬──────┘
                    │              │                  │
                    └──────────────┼──────────────────┘
                                   │
                          ┌────────▼────────┐
                          │ rules_loader.py │
                          │ + rules/*.yaml  │
                          └─────────────────┘

Phase 2: GitHub Action ──► scanner (same imports)
Phase 3: Next API route ──► subprocess python -m secmcp.scanner OR HTTP sidecar
```

## 2. Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `rules_loader.py` | Load YAML, compile regex, validate severity enum |
| `secrets.py` | Run `category: secrets` rules |
| `vibe_bugs.py` | Non-secret rules + small built-in line checks |
| `api_keys.py` | Provider HTTP validation, mask, cache |
| `scoring.py` | Weighted penalties → breakdown + overall |
| `scanner.py` | `resolve_content`, sync/async entrypoints |
| `server.py` | MCP tool registration, ToolError mapping |

## 3. Data Shapes (tool responses)

### Finding

```json
{
  "rule": "openai_api_key",
  "severity": "critical",
  "category": "secrets",
  "message": "…",
  "recommendation": "…",
  "location": { "file": "<snippet>", "line": 1, "column": 1 }
}
```

### API key validation

```json
{
  "provider": "openai",
  "status": "valid",
  "masked_key": "sk-a…xyz9",
  "message": "OpenAI key is valid."
}
```

### Security score

```json
{
  "overall_score": 88.0,
  "grade": "B",
  "breakdown": {
    "secrets": { "score": 100, "finding_count": 0, "findings": [] },
    "api_keys": { "score": 100, "finding_count": 0, "findings": [] },
    "configuration": { "score": 88, "finding_count": 1, "findings": [] },
    "code_quality": { "score": 100, "finding_count": 0, "findings": [] }
  },
  "summary": "…"
}
```

## 4. Phase 3 Database (Supabase) — draft schema

**Table: `scans`**

| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| user_id | uuid FK auth.users | |
| created_at | timestamptz | |
| source_type | text | `upload` \| `github` |
| source_label | text | repo name or filename |
| overall_score | numeric | |
| grade | text | |
| breakdown | jsonb | counts only; no raw secrets |
| finding_count | int | |

**Table: `findings`** (optional normalized)

| Column | Type |
|--------|------|
| scan_id | uuid FK |
| severity | text |
| rule | text |
| message | text |
| file | text |
| line | int |

**RLS:** users read/write own `scans` only.

## 5. API Routes (Phase 3 sketch)

| Method | Path | Action |
|--------|------|--------|
| POST | `/api/scan` | body: code or storage ref → run scanner |
| GET | `/api/scans` | list history |
| GET | `/api/scans/[id]` | detail |

No endpoint returns full API keys.

## 6. GitHub Action (Phase 2 sketch)

- Checkout repo
- `pip install` secmcp package
- Walk tree (exclude `node_modules`, `.git`, venv)
- Aggregate findings
- `gh issue create` or update label `secmcp`

## 7. Error Handling

| Case | MCP behavior |
|------|----------------|
| Missing input | ToolError |
| File not found | ToolError |
| Bad YAML | warnings in response; skip bad rules |
| Provider timeout | `network_error` on validate |

## 8. Extension Points

- Add `rules/custom.yaml` — no code change
- New provider: extend `api_keys.py` + doc
- New MCP tool: add function in `server.py` + scanner helper

## 9. What we do not store (MVP)

- Full file contents on server disk (Phase 1 MCP)
- Raw matched secret strings in logs
- API keys in Supabase (Phase 3 stores scores/metadata only)
