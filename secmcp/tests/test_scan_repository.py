"""
Prompt J — repository walk matches parity fixture scope.

Spec: prompts-directory-main/test.md (G3, G6)
Skills: .agents/skills/secmcp/SKILL.md, secret-scanning (no real tokens in tests)
Baseline: prompts-directory-main/examples/parity-mcp-guard.md

Live GitHub token validation (validate_api_key) is intentionally not covered here.
If GITHUB_TOKEN is unset, do not add a mock value to .env — static YAML rules only.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from secmcp.repo_walk import SKIP_DIRS
from secmcp.scanner import get_rules, scan_repository_sync

REPO_ROOT = Path(__file__).resolve().parents[2]
UNSAFE_FIXTURE = REPO_ROOT / "vendor" / "mcp-guard" / "examples" / "unsafe-mcp-config"

# Locked from parity-mcp-guard.md (whole unsafe-mcp-config tree via repo walk).
EXPECTED_WHOLE_FIXTURE_FINDINGS = 7
EXPECTED_MIN_FILES_SCANNED = 2

# Vendor parity fixture literals — findings must not echo these (test.md G3).
FIXTURE_LITERALS = (
    "fc_fake_example_key_1234567890",
    "qd_fake_example_key_1234567890",
    "correct-horse-battery-staple",
)


@pytest.fixture(scope="module")
def unsafe_fixture() -> Path:
    if not UNSAFE_FIXTURE.is_dir():
        pytest.skip(f"mcp-guard unsafe fixture missing: {UNSAFE_FIXTURE}")
    return UNSAFE_FIXTURE


def test_scan_repository_on_mcp_guard_fixture(unsafe_fixture: Path) -> None:
    result = scan_repository_sync(unsafe_fixture)
    assert result["files_scanned"] >= EXPECTED_MIN_FILES_SCANNED
    assert result["count"] >= EXPECTED_WHOLE_FIXTURE_FINDINGS
    assert "overall_score" in result
    assert "grade" in result
    assert "breakdown" in result
    assert "summary" in result
    assert isinstance(result["overall_score"], (int, float))
    assert result["grade"] in {"A", "B", "C", "D", "F"}


def test_prompt_j_whole_fixture_count_matches_parity_doc(unsafe_fixture: Path) -> None:
    result = scan_repository_sync(unsafe_fixture)
    assert result["count"] == EXPECTED_WHOLE_FIXTURE_FINDINGS


def test_scan_repository_returns_root_and_skip_metadata(unsafe_fixture: Path) -> None:
    result = scan_repository_sync(unsafe_fixture)
    assert result["root"] == str(unsafe_fixture.resolve())
    assert isinstance(result["files_scanned"], int)
    assert isinstance(result["files_skipped"], int)
    assert result["files_scanned"] >= 1
    assert "severity_counts" in result
    assert sum(result["severity_counts"].values()) == result["count"]


def test_scan_repository_no_raw_secret_literals_in_findings(unsafe_fixture: Path) -> None:
    result = scan_repository_sync(unsafe_fixture)
    blob = str(result.get("findings", []))
    for literal in FIXTURE_LITERALS:
        assert literal not in blob


def test_scan_repository_finding_rules_from_yaml_catalog(tmp_path: Path) -> None:
    """Detection uses declarative rules (default-rules.yaml), not hardcoded strings in scanner."""
    rules, _warnings = get_rules()
    rule_names = {r.name for r in rules}
    assert "openai_api_key" in rule_names
    assert "github_pat" in rule_names

    sample = tmp_path / "config.py"
    sample.write_text(
        'OPENAI_API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz123456"\n',
        encoding="utf-8",
    )
    result = scan_repository_sync(tmp_path)
    assert result["count"] >= 1
    reported = {f.get("rule") for f in result["findings"]}
    assert reported <= rule_names
    assert "openai_api_key" in reported


def test_scan_repository_detects_github_pat_via_yaml_rule(tmp_path: Path) -> None:
    """GitHub PAT shape comes from github_pat rule in YAML — no GITHUB_TOKEN / .env mock."""
    rules, _ = get_rules()
    rule_names = {r.name for r in rules}
    fake_pat = "ghp_" + "a" * 36
    (tmp_path / "settings.env").write_text(f"GITHUB_TOKEN={fake_pat}\n", encoding="utf-8")

    result = scan_repository_sync(tmp_path)
    rules_hit = {f.get("rule") for f in result["findings"]}
    assert "github_pat" in rules_hit
    assert rules_hit <= rule_names
    assert fake_pat not in str(result["findings"])


def test_scan_repository_skips_mcp_guard_skip_dirs(tmp_path: Path) -> None:
    """SKIP_DIRS aligned with vendor/mcp-guard (MIT) — see secmcp/repo_walk.py."""
    assert "node_modules" in SKIP_DIRS
    ignored = tmp_path / "node_modules"
    ignored.mkdir()
    (ignored / "package.js").write_text(
        'const token = "sk-proj-abcdefghijklmnopqrstuvwxyz123456";',
        encoding="utf-8",
    )
    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text("print('hello')", encoding="utf-8")

    result = scan_repository_sync(tmp_path)
    assert result["files_scanned"] == 1
    assert result["count"] == 0


def test_scan_repository_skips_binary_extension(tmp_path: Path) -> None:
    (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
    (tmp_path / "readme.txt").write_text("no secrets here\n", encoding="utf-8")

    result = scan_repository_sync(tmp_path)
    assert result["files_scanned"] == 1
    assert result["count"] == 0


def test_scan_repository_respects_mcpguardignore(tmp_path: Path) -> None:
    """L7 parity with vendor/mcp-guard — directory patterns skip fixture trees."""
    (tmp_path / ".mcpguardignore").write_text(
        "\n".join(
            [
                "# Test fixtures intentionally use fake secrets.",
                "tests/",
            ]
        ),
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_fixture.py").write_text(
        'OPENAI_API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz123456"\n',
        encoding="utf-8",
    )
    (tmp_path / ".env").write_text(
        "ANTHROPIC_API_KEY=sk-ant-abcdefghijklmnopqrstuvwxyz123456\n",
        encoding="utf-8",
    )

    result = scan_repository_sync(tmp_path)
    assert result["files_skipped"] == 1
    assert result["count"] == 1
    rules_hit = {f.get("rule") for f in result["findings"]}
    assert rules_hit == {"anthropic_api_key"}
    assert "openai_api_key" not in rules_hit


def test_scan_repository_includes_interactive_graph(unsafe_fixture: Path) -> None:
    result = scan_repository_sync(unsafe_fixture)
    assert "interactive_graph" in result
    assert "flowchart TB" in result["interactive_graph"]
    assert "```mermaid" in result.get("detailed_report", "")
