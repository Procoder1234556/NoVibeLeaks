"""
Prompt K — mcp-guard parity (automated acceptance).

Manual workflow: prompts-directory-main/AGENT_PROMPTS.md § Prompt K
Baseline counts: prompts-directory-main/examples/parity-mcp-guard.md

Requires: pip install -e vendor/mcp-guard  (optional; tests skip if missing)
          pip install -e secmcp
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from secmcp.scanner import check_secrets_sync, scan_vibe_bugs_sync

_HAS_MCP_GUARD = importlib.util.find_spec("mcp_guard") is not None
requires_mcp_guard = pytest.mark.skipif(
    not _HAS_MCP_GUARD,
    reason="pip install -e ../vendor/mcp-guard for mcp-guard parity assertions",
)

# Repo root: secmcp/tests/ -> secmcp/ -> repo
REPO_ROOT = Path(__file__).resolve().parents[2]
UNSAFE_FIXTURE = REPO_ROOT / "vendor" / "mcp-guard" / "examples" / "unsafe-mcp-config"
MCP_JSON = UNSAFE_FIXTURE / ".cursor" / "mcp.json"
ENV_EXAMPLE = UNSAFE_FIXTURE / ".env.example"

# Locked baseline from parity-mcp-guard.md (re-run Prompt K to refresh).
EXPECTED_MCP_GUARD_MCP_JSON = 2
EXPECTED_MCP_GUARD_ENV = 4
EXPECTED_MCP_GUARD_WHOLE_FIXTURE = 6

EXPECTED_SECMCP_VIBE_MCP_JSON = 3
EXPECTED_SECMCP_SECRETS_MCP_JSON = 0
EXPECTED_SECMCP_SECRETS_ENV = 4
EXPECTED_SECMCP_COMBINED_FIXTURE = 7


@pytest.fixture(scope="module")
def fixture_paths() -> tuple[Path, Path, Path]:
    if not UNSAFE_FIXTURE.is_dir():
        pytest.skip(f"mcp-guard unsafe fixture missing: {UNSAFE_FIXTURE}")
    if not MCP_JSON.is_file() or not ENV_EXAMPLE.is_file():
        pytest.skip("unsafe-mcp-config fixture files incomplete")
    return UNSAFE_FIXTURE, MCP_JSON, ENV_EXAMPLE


def _mcp_guard_count(root: Path, *, include_files: list[Path] | None = None) -> int:
    from mcp_guard.scanner import scan_path

    result = scan_path(root, include_files=include_files)
    return len(result.findings)


def test_prompt_k_fixture_present(fixture_paths: tuple[Path, Path, Path]) -> None:
    root, mcp, env = fixture_paths
    assert root.name == "unsafe-mcp-config"
    assert mcp.suffix == ".json"
    assert env.name == ".env.example"


@requires_mcp_guard
def test_prompt_k_mcp_json_mcp_guard_matches_baseline(
    fixture_paths: tuple[Path, Path, Path],
) -> None:
    root, mcp, _ = fixture_paths
    assert _mcp_guard_count(root, include_files=[mcp]) == EXPECTED_MCP_GUARD_MCP_JSON


@requires_mcp_guard
def test_prompt_k_env_mcp_guard_matches_baseline(
    fixture_paths: tuple[Path, Path, Path],
) -> None:
    root, _, env = fixture_paths
    assert _mcp_guard_count(root, include_files=[env]) == EXPECTED_MCP_GUARD_ENV


@requires_mcp_guard
def test_prompt_k_whole_fixture_mcp_guard_matches_baseline(
    fixture_paths: tuple[Path, Path, Path],
) -> None:
    root, _, _ = fixture_paths
    assert _mcp_guard_count(root) == EXPECTED_MCP_GUARD_WHOLE_FIXTURE


def test_prompt_k_mcp_json_secmcp_scan_vibe_bugs_matches_baseline(
    fixture_paths: tuple[Path, Path, Path],
) -> None:
    _, mcp, _ = fixture_paths
    assert scan_vibe_bugs_sync(path=str(mcp))["count"] == EXPECTED_SECMCP_VIBE_MCP_JSON


def test_prompt_k_mcp_json_secmcp_check_secrets_is_zero(
    fixture_paths: tuple[Path, Path, Path],
) -> None:
    """MCP config paths use scan_vibe_bugs, not YAML secret regex on quoted JSON."""
    _, mcp, _ = fixture_paths
    assert check_secrets_sync(path=str(mcp))["count"] == EXPECTED_SECMCP_SECRETS_MCP_JSON


def test_prompt_k_env_secmcp_check_secrets_matches_mcp_guard(
    fixture_paths: tuple[Path, Path, Path],
) -> None:
    _, _, env = fixture_paths
    assert check_secrets_sync(path=str(env))["count"] == EXPECTED_SECMCP_SECRETS_ENV


def test_prompt_k_combined_secmcp_covers_fixture_scope(
    fixture_paths: tuple[Path, Path, Path],
) -> None:
    """Parity doc sum (env secrets + MCP vibe); full tree walk: test_scan_repository.py."""
    _, mcp, env = fixture_paths
    combined = check_secrets_sync(path=str(env))["count"] + scan_vibe_bugs_sync(path=str(mcp))["count"]
    assert combined == EXPECTED_SECMCP_COMBINED_FIXTURE


@requires_mcp_guard
def test_prompt_k_secmcp_secret_count_at_least_mcp_guard_on_env(
    fixture_paths: tuple[Path, Path, Path],
) -> None:
    root, _, env = fixture_paths
    guard_env = _mcp_guard_count(root, include_files=[env])
    secmcp_env = check_secrets_sync(path=str(env))["count"]
    assert secmcp_env >= guard_env


def test_prompt_k_no_raw_secret_values_in_secmcp_findings(
    fixture_paths: tuple[Path, Path, Path],
) -> None:
    """Parity doc policy: masked output only; findings must not echo fixture literals."""
    _, mcp, env = fixture_paths
    suspicious = (
        "fc_fake_example_key_1234567890",
        "qd_fake_example_key_1234567890",
        "correct-horse-battery-staple",
    )
    for result in (
        check_secrets_sync(path=str(env)),
        scan_vibe_bugs_sync(path=str(mcp)),
    ):
        blob = str(result.get("findings", []))
        for literal in suspicious:
            assert literal not in blob
