"""MCP client config checks (patterns informed by vendor/mcp-guard, MIT)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

MCP_CONFIG_NAMES = frozenset({"mcp.json", "claude_desktop_config.json", ".mcp.json"})
MCP_CONFIG_SUFFIXES = (
    os.path.join(".cursor", "mcp.json"),
    os.path.join(".vscode", "mcp.json"),
)

MCP_SECRET_KEYS = frozenset(
    {"api_key", "apikey", "api-key", "key", "token", "access_token", "auth_token", "password", "secret"}
)

# ponytail: high-signal shell-injection signals in MCP args (aligned with mcp-security-audit skill)
_DANGEROUS_ARG_PATTERNS: list[tuple[str, str, str]] = [
    (r"\$\(", "high", "Command substitution in MCP server args."),
    (r"`[^`]+`", "high", "Backtick command substitution in MCP server args."),
    (r"(?i)bash\s+-c\s", "high", "bash -c in MCP server args."),
    (r"(?i)sh\s+-c\s", "high", "sh -c in MCP server args."),
    (r";\s*\w", "medium", "Possible command chaining (;) in MCP server args."),
    (r"\|\s*\w", "medium", "Possible pipe in MCP server args."),
]

_NPX_MUTABLE = re.compile(
    r"^(npx|bunx|pnpm|yarn)(\s|$)",
    re.I,
)


def is_mcp_config_path(path: str | Path) -> bool:
    p = Path(path)
    normalized = os.path.normpath(str(p))
    if p.name in MCP_CONFIG_NAMES:
        return True
    return any(normalized.endswith(suffix) for suffix in MCP_CONFIG_SUFFIXES)


def _is_mcp_config_document(text: str, source: str) -> bool:
    """True only for MCP config files or parseable JSON with a root mcpServers object."""
    if is_mcp_config_path(source):
        return True
    stripped = text.lstrip()
    if not stripped.startswith("{") or "mcpServers" not in text:
        return False
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return False
    return isinstance(parsed, dict) and "mcpServers" in parsed


def scan_mcp_config_text(text: str, source: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not _is_mcp_config_document(text, source):
        return findings

    findings.extend(_scan_json_structure(text, source))
    findings.extend(_scan_args_injection(text, source))
    findings.extend(_scan_mutable_runners(text, source))
    return findings


def _finding(
    rule: str,
    severity: str,
    message: str,
    recommendation: str,
    source: str,
    line: int,
    column: int,
    category: str = "configuration",
) -> dict[str, Any]:
    return {
        "rule": rule,
        "severity": severity,
        "category": category,
        "message": message,
        "recommendation": recommendation,
        "location": {"file": source, "line": line, "column": column},
    }


def _line_column(text: str, index: int) -> tuple[int, int]:
    line = text.count("\n", 0, index) + 1
    col = index - text.rfind("\n", 0, index)
    return line, max(col, 1)


def _walk_json(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    out: list[tuple[tuple[str, ...], Any]] = []
    if isinstance(value, dict):
        for k, v in value.items():
            out.extend(_walk_json(v, path + (str(k),)))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            out.extend(_walk_json(v, path + (str(i),)))
    else:
        out.append((path, value))
    return out


def _looks_like_secret(value: str) -> bool:
    s = value.strip()
    if len(s) < 12:
        return False
    if s.lower() in {"changeme", "your_api_key", "your-api-key", "example", "password"}:
        return False
    return True


def _scan_json_structure(text: str, source: str) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return []

    findings: list[dict[str, Any]] = []
    for key_path, value in _walk_json(parsed):
        if not isinstance(value, str) or not _looks_like_secret(value):
            continue
        key = key_path[-1].lower() if key_path else ""
        if key not in MCP_SECRET_KEYS and not any(t in key for t in MCP_SECRET_KEYS):
            continue
        if value.startswith("${") and value.endswith("}"):
            continue
        idx = text.find(value)
        line, col = _line_column(text, idx if idx >= 0 else 0)
        findings.append(
            _finding(
                "mcp_config_literal_secret",
                "critical",
                f"Literal secret in MCP config at {'/'.join(key_path)}.",
                "Use host environment variables; never commit credentials in mcp.json.",
                source,
                line,
                col,
            )
        )
    return findings


def _scan_args_injection(text: str, source: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for pattern, severity, message in _DANGEROUS_ARG_PATTERNS:
        for match in re.finditer(pattern, text):
            line, col = _line_column(text, match.start())
            findings.append(
                _finding(
                    "mcp_args_shell_injection",
                    severity,
                    message,
                    "Use direct command + args array; avoid shell interpolation in MCP config.",
                    source,
                    line,
                    col,
                )
            )
    return findings


def _scan_mutable_runners(text: str, source: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if "@latest" in text.lower():
        for match in re.finditer(r"@latest", text, re.I):
            line, col = _line_column(text, match.start())
            findings.append(
                _finding(
                    "mcp_mutable_package_ref",
                    "medium",
                    "Mutable package reference (@latest) in MCP config.",
                    "Pin MCP server package to an exact reviewed version.",
                    source,
                    line,
                    col,
                )
            )
    if re.search(r'"command"\s*:\s*"npx"', text, re.I) and "@latest" not in text.lower():
        if not re.search(r"@[0-9]+\.[0-9]+\.[0-9]+", text):
            findings.append(
                _finding(
                    "mcp_unpinned_npx",
                    "medium",
                    "npx-based MCP server without obvious exact version pin.",
                    "Prefer python/uv path to local server.py or pin package@x.y.z.",
                    source,
                    1,
                    1,
                )
            )
    return findings
