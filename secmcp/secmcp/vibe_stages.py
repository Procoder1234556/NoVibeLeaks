"""Vibe-coder journey stages — detailed, coach-style scan narratives."""

from __future__ import annotations

import re
from typing import Any

from secmcp.reporting import attach_interactive_graph

# The 15 stages (Nikunj / vibe-coder backend meme — used as a teaching frame, not mockery).
STAGES: list[dict[str, str]] = [
    {
        "stage": "1",
        "title": 'Just use localStorage, it\'s fine',
        "lesson": "Secrets and session tokens belong server-side; browsers are untrusted.",
    },
    {
        "stage": "2",
        "title": "Okay, let's add a real database",
        "lesson": "Pick storage for access patterns; don't skip connection pooling and env-based config.",
    },
    {
        "stage": "3",
        "title": "Picks Supabase because of a tweet",
        "lesson": "Managed Postgres is fine — still design schema, keys, and policies deliberately.",
    },
    {
        "stage": "4",
        "title": "Forgets to turn on row level security",
        "lesson": "Enable RLS on user-owned tables; service role keys never ship to the client.",
    },
    {
        "stage": "5",
        "title": "API keys pushed to a public GitHub repo",
        "lesson": "Rotate exposed keys; use env/CI secrets; enable push protection.",
    },
    {
        "stage": "6",
        "title": 'Why is my OpenAI bill $847?',
        "lesson": "Keys in client code or logs get scraped; rate-limit and monitor provider usage.",
    },
    {
        "stage": "7",
        "title": 'Asks the AI to "make it secure"',
        "lesson": "Security is incremental — fix highest-risk items with tests, not a blind rewrite.",
    },
    {
        "stage": "8",
        "title": "It rewrites the entire backend",
        "lesson": "Large unreviewed diffs hide regressions; fence scope and ship small PRs.",
    },
    {
        "stage": "9",
        "title": "Nothing works anymore",
        "lesson": "Stabilize with smoke tests and rollbacks before more features.",
    },
    {
        "stage": "10",
        "title": "Reverts to 3 days ago",
        "lesson": "Git history isn't a backup strategy — tag releases and keep migrations reversible.",
    },
    {
        "stage": "11",
        "title": "Adds auth. Breaks login for everyone",
        "lesson": "Auth changes need session/cookie contracts and a migration path for users.",
    },
    {
        "stage": "12",
        "title": 'Who needs migrations?',
        "lesson": "Schema changes need versioned migrations; never hand-edit prod.",
    },
    {
        "stage": "13",
        "title": "Production database deleted by an agent",
        "lesson": "Agents need least-privilege DB creds; no destructive tools on prod.",
    },
    {
        "stage": "14",
        "title": "Learns what a backup is",
        "lesson": "Enable PITR/backups before you need them; test a restore once.",
    },
    {
        "stage": "15",
        "title": "Hires a backend engineer",
        "lesson": "You're reading SecMCP early — fix stages 4–6 before stage 8.",
    },
]

_RULE_STAGE: dict[str, int] = {
    "openai_api_key": 6,
    "anthropic_api_key": 6,
    "stripe_secret_key": 5,
    "stripe_test_secret": 5,
    "aws_access_key_id": 5,
    "github_pat": 5,
    "github_oauth": 5,
    "generic_private_key": 5,
    "postgres_url_in_source": 4,
    "postgres_url": 4,
    "database_url": 4,
    "requests_verify_false": 7,
    "cors_allow_all": 11,
    "eval_usage": 7,
    "exec_usage": 7,
    "sql_string_concat": 12,
    "dangerously_set_inner_html": 1,
    "pickle_untrusted": 7,
    "mcp_env_literal_secret": 5,
    "mcp_injection_pattern": 13,
    "mcp_npx_unpinned": 13,
}

_TEXT_SIGNALS: list[tuple[int, re.Pattern[str], str]] = [
    (
        1,
        re.compile(r"localStorage\.(setItem|getItem)\s*\([^)]*(?:api[_-]?key|token|secret)", re.I),
        "API key or token stored in localStorage",
    ),
    (
        3,
        re.compile(r"supabase", re.I),
        "Supabase client or URL referenced",
    ),
    (
        4,
        re.compile(r"createClient\s*\(", re.I),
        "Supabase createClient without visible RLS policy setup in this snippet",
    ),
    (
        4,
        re.compile(r"service_role|SUPABASE_SERVICE_ROLE", re.I),
        "Service-role Supabase key may be exposed to the wrong tier",
    ),
    (
        12,
        re.compile(r"DROP\s+TABLE|TRUNCATE\s+", re.I),
        "Destructive SQL in application code",
    ),
    (
        13,
        re.compile(r"(?i)rm\s+-rf\s+/|drop\s+database|prisma\s+db\s+push\s+--accept-data-loss"),
        "Destructive shell/SQL pattern friendly to agents",
    ),
]

_MCP_DANGEROUS_RULES = frozenset(
    {
        "mcp_injection_pattern",
        "mcp_env_literal_secret",
        "mcp_npx_unpinned",
    }
)


def _stage_meta(n: int) -> dict[str, str]:
    idx = max(1, min(n, len(STAGES))) - 1
    row = STAGES[idx]
    return {"stage": row["stage"], "title": row["title"], "lesson": row["lesson"]}


def _finding_stage(finding: dict[str, Any]) -> int | None:
    rule = str(finding.get("rule") or "")
    if rule in _RULE_STAGE:
        return _RULE_STAGE[rule]
    if rule.startswith("api_key_"):
        return 6
    cat = str(finding.get("category") or "").lower()
    sev = str(finding.get("severity") or "").lower()
    if cat == "secrets":
        return 5
    if rule in _MCP_DANGEROUS_RULES:
        return 13
    if cat == "configuration" and sev in ("critical", "high"):
        return 7
    return None


def _text_signals(text: str, source: str) -> list[dict[str, Any]]:
    if not text.strip():
        return []
    has_rls = bool(re.search(r"\brow\s+level\s+security\b|\benable\s+rls\b|\bPOLICY\b", text, re.I))
    hits: list[dict[str, Any]] = []
    for stage, pattern, desc in _TEXT_SIGNALS:
        if not pattern.search(text):
            continue
        if stage == 4 and has_rls:
            continue
        hits.append(
            {
                "stage": stage,
                "evidence": desc,
                "source": source,
                "rule": "text_signal",
            }
        )
    return hits


def _collect_triggered(
    findings: list[dict[str, Any]],
    text: str,
    source: str,
    api_results: list[dict[str, Any]] | None,
) -> dict[int, list[dict[str, Any]]]:
    by_stage: dict[int, list[dict[str, Any]]] = {}
    for f in findings:
        stage = _finding_stage(f)
        if stage is None:
            continue
        loc = f.get("location") or {}
        by_stage.setdefault(stage, []).append(
            {
                "rule": f.get("rule"),
                "severity": f.get("severity"),
                "message": f.get("message"),
                "recommendation": f.get("recommendation"),
                "file": loc.get("file") or source,
                "line": loc.get("line"),
            }
        )
    for hit in _text_signals(text, source):
        by_stage.setdefault(int(hit["stage"]), []).append(hit)

    for r in api_results or []:
        if r.get("status") == "valid":
            by_stage.setdefault(6, []).append(
                {
                    "rule": f"api_key_{r.get('provider', 'unknown')}",
                    "severity": "critical",
                    "message": "Live API key present in scanned material (validated).",
                    "recommendation": "Rotate if ever committed; move to env; add usage alerts.",
                }
            )
        elif r.get("status") == "invalid":
            by_stage.setdefault(5, []).append(
                {
                    "rule": f"api_key_{r.get('provider', 'unknown')}",
                    "severity": "high",
                    "message": r.get("message", "Invalid or revoked key still referenced."),
                    "recommendation": "Remove dead keys from code and secret stores.",
                }
            )
    return by_stage


_SEVERITY_ORDER = ("critical", "high", "medium", "low")


def _severity_counts(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {s: 0 for s in _SEVERITY_ORDER}
    for f in findings:
        sev = str(f.get("severity", "medium")).lower()
        if sev in counts:
            counts[sev] += 1
        else:
            counts[sev] = counts.get(sev, 0) + 1
    return counts


def _sort_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(f: dict[str, Any]) -> tuple[int, str, int]:
        sev = str(f.get("severity", "medium")).lower()
        idx = _SEVERITY_ORDER.index(sev) if sev in _SEVERITY_ORDER else 99
        loc = f.get("location") or {}
        return (idx, str(loc.get("file", "")), int(loc.get("line") or 0))

    return sorted(findings, key=key)


def _priority_fixes(by_stage: dict[int, list[dict[str, Any]]], findings: list[dict[str, Any]]) -> list[str]:
    fixes: list[str] = []
    seen: set[str] = set()
    order = sorted(by_stage.keys())
    for stage in order:
        for item in by_stage[stage]:
            rec = str(item.get("recommendation") or item.get("message") or "").strip()
            if rec and rec not in seen:
                seen.add(rec)
                fixes.append(rec)
    if len(fixes) < 3:
        for f in sorted(findings, key=lambda x: str(x.get("severity")))[:5]:
            rec = str(f.get("recommendation") or "").strip()
            if rec and rec not in seen:
                seen.add(rec)
                fixes.append(rec)
    return fixes[:7]


def build_vibe_report(
    *,
    findings: list[dict[str, Any]],
    text: str = "",
    source: str = "<snippet>",
    overall_score: float | None = None,
    grade: str | None = None,
    api_results: list[dict[str, Any]] | None = None,
    breakdown: dict[str, Any] | None = None,
    summary: str | None = None,
    severity_counts: dict[str, int] | None = None,
    rules_load_warnings: list[str] | None = None,
    scan_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Coach-style narrative for MCP and web clients."""
    by_stage = _collect_triggered(findings, text, source, api_results)
    if not by_stage and (overall_score is not None and overall_score >= 90):
        current = 15
    elif not by_stage:
        current = 2
    else:
        current = max(by_stage.keys())

    meta = _stage_meta(current)
    triggered = [
        {
            **_stage_meta(stage),
            "signals": stage_items[:10],
            "signal_count": len(stage_items),
        }
        for stage, stage_items in sorted(by_stage.items())
    ]

    score_line = ""
    if overall_score is not None:
        score_line = f"**Score:** {overall_score}/100 (grade {grade or '—'}).\n\n"

    sev = severity_counts if severity_counts is not None else _severity_counts(findings)

    lines = [
        "## SecMCP scan report",
        "",
        f"**Scope:** `{source}`",
        f"**Findings:** {len(findings)}",
        "",
        "## Vibe-coder backend check-in",
        "",
        score_line + f"**You're roughly at stage {meta['stage']}/15:** _{meta['title']}_",
        "",
        f"_{meta['lesson']}_",
        "",
    ]

    if summary:
        lines.extend(["### Executive summary", "", summary, ""])

    if any(sev.values()):
        lines.extend(
            [
                "### Severity",
                "",
                "| Severity | Count |",
                "|----------|-------|",
            ]
        )
        for level in _SEVERITY_ORDER:
            if sev.get(level):
                lines.append(f"| {level.title()} | {sev[level]} |")
        lines.append("")

    if breakdown:
        lines.extend(["### Score breakdown (0–100 per bucket)", "", "| Bucket | Score | Issues |", "|--------|-------|--------|"])
        for bucket, data in breakdown.items():
            if not isinstance(data, dict):
                continue
            lines.append(
                f"| {bucket.replace('_', ' ').title()} | {data.get('score', '—')} | {data.get('finding_count', 0)} |"
            )
        lines.append("")

    if api_results:
        lines.extend(["### Live API key checks", "", "| Provider | Status | Key | Detail |", "|----------|--------|-----|--------|"])
        for r in api_results:
            lines.append(
                f"| {r.get('provider', '?')} | {r.get('status', '?')} | {r.get('masked_key', '****')} | {r.get('message', '')} |"
            )
        lines.append("")

    sorted_findings = _sort_findings(findings)
    if sorted_findings:
        lines.extend(["### Findings (detail)", ""])
        for idx, f in enumerate(sorted_findings[:20], start=1):
            loc = f.get("location") or {}
            file_line = f"{loc.get('file', source)}:{loc.get('line', '?')}"
            sev_label = str(f.get("severity", "medium")).title()
            rule = f.get("rule", "unknown")
            stage_bit = ""
            if f.get("vibe_stage"):
                stage_bit = f" — stage {f['vibe_stage']}"
            lines.append(f"#### {idx}. [{sev_label}] `{rule}`{stage_bit}")
            lines.append("")
            lines.append(f"- **Location:** `{file_line}`")
            if f.get("message"):
                lines.append(f"- **Issue:** {f.get('message')}")
            if f.get("recommendation"):
                lines.append(f"- **Fix:** {f.get('recommendation')}")
            lines.append("")
        if len(sorted_findings) > 20:
            lines.append(f"_…and {len(sorted_findings) - 20} more finding(s)._")
            lines.append("")

    if rules_load_warnings:
        lines.extend(["### Rules loader warnings", ""])
        for w in rules_load_warnings:
            lines.append(f"- {w}")
        lines.append("")

    if scan_meta:
        meta_bits = [f"- **{k}:** {v}" for k, v in scan_meta.items() if v is not None]
        if meta_bits:
            lines.extend(["### Scan metadata", ""] + meta_bits + [""])

    if triggered:
        lines.append("### Stages this scan lights up")
        lines.append("")
        for block in triggered:
            lines.append(
                f"- **Stage {block['stage']} — {block['title']}** ({block['signal_count']} signal(s))"
            )
        lines.append("")

    fixes = _priority_fixes(by_stage, findings)
    if fixes:
        lines.extend(["### Do this next (smallest safe steps)", ""])
        for i, fix in enumerate(fixes, start=1):
            lines.append(f"{i}. {fix}")
        lines.append("")

    lines.extend(
        [
            "### Nikunj backend gate (before the next AI rewrite)",
            "",
            "- Name your **critical write** (one mutation that must never double-apply).",
            "- Separate **read path** vs **write path**; fix secrets and RLS on the write path first.",
            "- Ship **one PR** per risk class (secrets → RLS → auth → SQL), with pytest/smoke tests.",
            "",
            "_Which stage are you on? Fix stage 4–6 before letting an agent rewrite the world._",
        ]
    )

    execution_summary = {
        "source": source,
        "finding_count": len(findings),
        "severity_counts": sev,
        "overall_score": overall_score,
        "grade": grade,
        "vibe_stage": int(meta["stage"]),
        "api_key_checks": len(api_results or []),
    }
    if breakdown:
        execution_summary["breakdown_scores"] = {
            k: (v.get("score") if isinstance(v, dict) else None) for k, v in breakdown.items()
        }
    if scan_meta:
        execution_summary.update({k: v for k, v in scan_meta.items() if v is not None})

    return {
        "vibe_stage": int(meta["stage"]),
        "vibe_stage_title": meta["title"],
        "vibe_stage_lesson": meta["lesson"],
        "vibe_stages_catalog": STAGES,
        "vibe_stages_triggered": triggered,
        "priority_fixes": fixes,
        "severity_counts": sev,
        "execution_summary": execution_summary,
        "detailed_report": "\n".join(lines),
        "coach_prompt": (
            f"Stage {meta['stage']}/15: {meta['title']}. "
            "Which stage are you on? Tackle priority_fixes before a big 'make it secure' rewrite."
        ),
    }


def annotate_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for f in findings:
        row = dict(f)
        stage = _finding_stage(f)
        if stage is not None:
            sm = _stage_meta(stage)
            row["vibe_stage"] = stage
            row["vibe_stage_title"] = sm["title"]
        out.append(row)
    return out


def enrich_scan_payload(
    payload: dict[str, Any],
    *,
    text: str = "",
    source: str = "<snippet>",
    findings: list[dict[str, Any]] | None = None,
    api_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Merge vibe narrative into an existing tool response dict."""
    merged = dict(payload)
    fs = findings if findings is not None else list(merged.get("findings") or [])
    annotated = annotate_findings(fs)
    merged["findings"] = annotated
    scan_meta: dict[str, Any] = {}
    if merged.get("root"):
        scan_meta["root"] = merged.get("root")
    if merged.get("files_scanned") is not None:
        scan_meta["files_scanned"] = merged.get("files_scanned")
    if merged.get("files_skipped") is not None:
        scan_meta["files_skipped"] = merged.get("files_skipped")

    report = build_vibe_report(
        findings=annotated,
        text=text,
        source=source,
        overall_score=merged.get("overall_score"),
        grade=merged.get("grade"),
        api_results=api_results,
        breakdown=merged.get("breakdown"),
        summary=merged.get("summary"),
        severity_counts=merged.get("severity_counts"),
        rules_load_warnings=merged.get("rules_load_warnings"),
        scan_meta=scan_meta or None,
    )
    merged.update(report)
    return attach_interactive_graph(merged)
