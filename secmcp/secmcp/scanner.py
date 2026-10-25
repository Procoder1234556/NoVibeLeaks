"""Shared scan orchestration for MCP, CI, and web."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from secmcp.api_keys import detect_provider, extract_key_from_code, validate_api_key
from secmcp.repo_walk import (
    is_ignored_path,
    iter_repo_files,
    load_ignore_patterns,
    relative_display_path,
    should_skip_file,
)
from secmcp.rules_loader import Rule, load_default_rules
from secmcp.reporting import write_vulnerabilities_txt_file
from secmcp.scoring import score_from_findings
from secmcp.secrets import scan_secrets
from secmcp.vibe_bugs import scan_vibe_bugs
from secmcp.vibe_stages import enrich_scan_payload

_RULES: list[Rule] | None = None
_RULE_ERRORS: list[str] | None = None


def get_rules() -> tuple[list[Rule], list[str]]:
    global _RULES, _RULE_ERRORS
    if _RULES is None:
        _RULES, _RULE_ERRORS = load_default_rules()
    return _RULES, _RULE_ERRORS or []


def _path_target(path: str) -> Path:
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    return p


def resolve_content(code: str | None, path: str | None) -> tuple[str, str]:
    """Return (text, source_label)."""
    if code and code.strip():
        label = path.strip() if path else "<snippet>"
        return code, label
    if path:
        p = _path_target(path)
        if p.is_dir():
            raise ValueError(
                f"Path is a directory: {path}. Use get_security_score(path=...) "
                "for a full repo walk, or pass a file path."
            )
        if not p.is_file():
            raise FileNotFoundError(f"Path is not a file: {path}")
        return p.read_text(encoding="utf-8", errors="replace"), str(p)
    raise ValueError("Provide code snippet or a readable file path.")


def _filter_repo_scan(
    full: dict[str, Any],
    *,
    category: str | None = None,
) -> dict[str, Any]:
    """Subset a repository scan payload (secrets-only or vibe-only)."""
    findings = list(full.get("findings") or [])
    if category == "secrets":
        findings = [f for f in findings if f.get("category") == "secrets"]
    elif category == "vibe":
        findings = [f for f in findings if f.get("category") != "secrets"]

    severity_counts: dict[str, int] = {}
    for item in findings:
        sev = str(item.get("severity", "medium"))
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    secret_findings = [f for f in findings if f.get("category") == "secrets"]
    vibe_findings = [f for f in findings if f.get("category") != "secrets"]
    scored = score_from_findings(secret_findings, vibe_findings, [])

    return enrich_scan_payload(
        {
            "root": full.get("root"),
            "files_scanned": full.get("files_scanned"),
            "files_skipped": full.get("files_skipped"),
            "findings": findings,
            "count": len(findings),
            "severity_counts": severity_counts,
            "rules_load_warnings": full.get("rules_load_warnings"),
            "overall_score": scored["overall_score"],
            "grade": scored["grade"],
            "breakdown": scored["breakdown"],
            "summary": scored["summary"],
        },
        text="",
        source=str(full.get("root") or ""),
        findings=findings,
    )


def _maybe_repo_scan(
    code: str | None,
    path: str | None,
    *,
    category: str | None = None,
) -> dict[str, Any] | None:
    if code and code.strip():
        return None
    if not path:
        return None
    p = _path_target(path)
    if not p.is_dir():
        return None
    full = scan_repository_sync(p)
    if category is None:
        return full
    return _filter_repo_scan(full, category=category)


def _attach_vulnerabilities_export(
    result: dict[str, Any],
    *,
    write_vulnerabilities_txt: bool,
    vulnerabilities_path: str | None,
) -> dict[str, Any]:
    if not write_vulnerabilities_txt:
        return result
    out = Path(vulnerabilities_path).expanduser() if vulnerabilities_path else None
    written = write_vulnerabilities_txt_file(result, out)
    merged = dict(result)
    merged["vulnerabilities_txt_path"] = str(written)
    merged["vulnerabilities_txt_written"] = True
    return merged


def check_secrets_sync(code: str | None = None, path: str | None = None) -> dict[str, Any]:
    repo = _maybe_repo_scan(code, path, category="secrets")
    if repo is not None:
        return repo
    text, source = resolve_content(code, path)
    rules, load_errors = get_rules()
    findings = scan_secrets(text, source, rules)
    return enrich_scan_payload(
        {
            "findings": findings,
            "count": len(findings),
            "rules_load_warnings": load_errors,
        },
        text=text,
        source=source,
        findings=findings,
    )


def scan_vibe_bugs_sync(code: str | None = None, path: str | None = None) -> dict[str, Any]:
    repo = _maybe_repo_scan(code, path, category="vibe")
    if repo is not None:
        return repo
    text, source = resolve_content(code, path)
    rules, load_errors = get_rules()
    findings = scan_vibe_bugs(text, source, rules)
    return enrich_scan_payload(
        {
            "findings": findings,
            "count": len(findings),
            "rules_load_warnings": load_errors,
        },
        text=text,
        source=source,
        findings=findings,
    )


async def validate_key_for_tool(
    provider: str | None,
    key: str | None,
    code: str | None = None,
    path: str | None = None,
    supabase_url: str | None = None,
    aws_secret: str | None = None,
) -> dict[str, Any]:
    resolved_key = (key or "").strip()
    prov = provider.lower().strip() if provider else None

    if not resolved_key and (code or path):
        text, _ = resolve_content(code, path)
        if prov:
            resolved_key = extract_key_from_code(text, prov) or ""
        else:
            resolved_key = extract_key_from_code(text, None) or ""
            if resolved_key:
                prov = detect_provider(resolved_key)

    if not prov and resolved_key:
        prov = detect_provider(resolved_key)
    if not prov:
        msg = "Could not determine provider. Pass provider and key, or embed a recognizable key in code."
        return {
            "provider": provider or "unknown",
            "status": "unknown",
            "masked_key": "****",
            "message": msg,
            "detailed_report": f"## API key validation\n\n**Status:** `unknown`\n\n{msg}",
            "execution_summary": {"provider": provider or "unknown", "status": "unknown"},
        }

    result = await validate_api_key(
        prov,
        resolved_key,
        supabase_url=supabase_url,
        aws_secret=aws_secret,
    )
    status = str(result.get("status", "unknown"))
    lines = [
        "## API key validation",
        "",
        f"**Provider:** {result.get('provider', prov)}",
        f"**Masked key:** {result.get('masked_key', '****')}",
        f"**Status:** `{status}`",
        "",
        str(result.get("message", "")),
        "",
    ]
    if status == "valid":
        lines.append(
            "_Key is live — if this came from source control, rotate immediately and use env/CI secrets._"
        )
    elif status == "invalid":
        lines.append("_Remove revoked keys from code and secret stores._")
    result["detailed_report"] = "\n".join(lines)
    result["execution_summary"] = {
        "provider": result.get("provider", prov),
        "status": status,
        "masked_key": result.get("masked_key"),
    }
    return result


async def security_score_async(
    code: str | None = None,
    path: str | None = None,
    validate_keys: bool = False,
    supabase_url: str | None = None,
    write_vulnerabilities_txt: bool = False,
    vulnerabilities_path: str | None = None,
) -> dict[str, Any]:
    repo = _maybe_repo_scan(code, path)
    if repo is not None:
        if validate_keys:
            # Live key checks require file/snippet text; repo walk stays static rules only.
            repo = dict(repo)
            repo.setdefault("rules_load_warnings", [])
            repo["rules_load_warnings"] = list(repo.get("rules_load_warnings") or []) + [
                "validate_keys ignored for directory scans (use a single file or snippet)."
            ]
        return _attach_vulnerabilities_export(
            repo,
            write_vulnerabilities_txt=write_vulnerabilities_txt,
            vulnerabilities_path=vulnerabilities_path,
        )

    text, source = resolve_content(code, path)
    rules, load_errors = get_rules()
    secrets = scan_secrets(text, source, rules)
    vibe = scan_vibe_bugs(text, source, rules)

    api_results: list[dict[str, Any]] = []
    if validate_keys:
        seen: set[str] = set()
        pending: list[tuple[str, str]] = []
        for rule in rules:
            if rule.category != "secrets":
                continue
            for match in rule._compiled.finditer(text):
                raw = match.group(0)
                if raw in seen:
                    continue
                seen.add(raw)
                prov = detect_provider(raw)
                if not prov:
                    continue
                pending.append((prov, raw))
        if pending:
            api_results = list(
                await asyncio.gather(
                    *[
                        validate_api_key(prov, raw, supabase_url=supabase_url)
                        for prov, raw in pending
                    ]
                )
            )

    scored = score_from_findings(secrets, vibe, api_results)
    all_findings = secrets + vibe
    result = enrich_scan_payload(
        {
            **scored,
            "source": source,
            "findings": all_findings,
            "count": len(all_findings),
            "rules_load_warnings": load_errors,
            "api_key_checks": api_results if validate_keys else [],
        },
        text=text,
        source=source,
        findings=all_findings,
        api_results=api_results if validate_keys else [],
    )
    return _attach_vulnerabilities_export(
        result,
        write_vulnerabilities_txt=write_vulnerabilities_txt,
        vulnerabilities_path=vulnerabilities_path,
    )


def scan_repository_sync(root: str | Path) -> dict[str, Any]:
    """Walk a repo tree and run secret + vibe scans per text file (Phase 2 CI entry)."""
    base = Path(root).expanduser().resolve()
    if not base.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    rules, load_errors = get_rules()
    ignore_patterns = load_ignore_patterns(base)
    findings: list[dict[str, Any]] = []
    files_scanned = 0
    files_skipped = 0

    for file_path in iter_repo_files(base):
        rel_path = relative_display_path(file_path, base)
        if is_ignored_path(rel_path, ignore_patterns):
            files_skipped += 1
            continue
        if should_skip_file(file_path):
            files_skipped += 1
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            files_skipped += 1
            continue

        files_scanned += 1
        source = str(file_path)
        findings.extend(scan_secrets(text, source, rules))
        findings.extend(scan_vibe_bugs(text, source, rules))

    severity_counts: dict[str, int] = {}
    for item in findings:
        sev = str(item.get("severity", "medium"))
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    secret_findings = [f for f in findings if f.get("category") == "secrets"]
    vibe_findings = [f for f in findings if f.get("category") != "secrets"]
    scored = score_from_findings(secret_findings, vibe_findings, [])

    return enrich_scan_payload(
        {
            "root": str(base),
            "files_scanned": files_scanned,
            "files_skipped": files_skipped,
            "findings": findings,
            "count": len(findings),
            "severity_counts": severity_counts,
            "rules_load_warnings": load_errors,
            "overall_score": scored["overall_score"],
            "grade": scored["grade"],
            "breakdown": scored["breakdown"],
            "summary": scored["summary"],
        },
        text="",
        source=str(base),
        findings=findings,
    )


def list_rules_summary() -> dict[str, Any]:
    rules, errors = get_rules()
    items = [
        {
            "name": r.name,
            "severity": r.severity,
            "category": r.category,
            "message": r.message,
        }
        for r in rules
    ]
    by_category: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        by_category.setdefault(str(item["category"]), []).append(item)

    lines = [
        "## SecMCP rule catalog",
        "",
        f"**Total rules loaded:** {len(items)}",
        "",
    ]
    if errors:
        lines.extend(["### Load warnings", ""])
        for w in errors:
            lines.append(f"- {w}")
        lines.append("")
    for cat in sorted(by_category.keys()):
        lines.append(f"### {cat.replace('_', ' ').title()} ({len(by_category[cat])})")
        lines.append("")
        for r in sorted(by_category[cat], key=lambda x: str(x["name"])):
            lines.append(
                f"- **{r['name']}** ({r['severity']}) — {r['message']}"
            )
        lines.append("")

    return {
        "rules": items,
        "count": len(items),
        "load_warnings": errors,
        "rules_by_category": by_category,
        "detailed_report": "\n".join(lines),
        "execution_summary": {"rule_count": len(items), "categories": list(by_category.keys())},
    }


def demo() -> None:
    out = check_secrets_sync(code='x = "sk-abcdefghijklmnopqrstuvwxyz123456"')
    assert out["count"] >= 1


if __name__ == "__main__":
    demo()
    print("scanner ok")
