"""Optional leakferret MCP binary bridge (RFC: prompts-directory-main/rfc/leakferret-adapter.md)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

_ENV_BIN = "SECMCP_LEAKFERRET_BIN"
_DEFAULT_TIMEOUT_S = 30


def leakferret_binary() -> Path | None:
    raw = os.environ.get(_ENV_BIN, "").strip()
    if not raw:
        return None
    path = Path(raw).expanduser()
    return path if path.is_file() else None


def leakferret_available() -> bool:
    return leakferret_binary() is not None


def _unavailable(reason: str) -> dict[str, Any]:
    return {"available": False, "error": reason}


def verify_finding_via_leakferret(finding: dict[str, Any]) -> dict[str, Any]:
    """Delegate live verify to leakferret when SECMCP_LEAKFERRET_BIN is set."""
    binary = leakferret_binary()
    if binary is None:
        return _unavailable(f"{_ENV_BIN} not set or file missing")

    # Stub: real JSON-RPC tools/call wiring lands in a follow-up; keep interface stable.
    return _unavailable("leakferret verify_finding subprocess bridge not implemented yet")


def baseline_diff_via_leakferret(repo_root: Path) -> dict[str, Any]:
    """Diff scan vs baseline via leakferret when binary is configured."""
    binary = leakferret_binary()
    if binary is None:
        return _unavailable(f"{_ENV_BIN} not set or file missing")
    return _unavailable("leakferret baseline_diff subprocess bridge not implemented yet")


def _run_json_rpc(binary: Path, payload: dict[str, Any], timeout_s: int = _DEFAULT_TIMEOUT_S) -> dict[str, Any]:
    """Run one JSON-RPC message on stdin; never log payload secrets."""
    proc = subprocess.run(
        [str(binary)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )
    if proc.returncode != 0:
        return {"ok": False, "stderr": (proc.stderr or "")[:500]}
    try:
        return {"ok": True, "body": json.loads(proc.stdout)}
    except json.JSONDecodeError:
        return {"ok": False, "stderr": "invalid JSON on stdout"}
