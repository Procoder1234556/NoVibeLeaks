"""
L2 — false-positive regression on three in-repo sample trees.

Baseline doc: prompts-directory-main/examples/fp-review-samples.md
"""

from __future__ import annotations

from pathlib import Path

from secmcp.scanner import scan_repository_sync

REPO_ROOT = Path(__file__).resolve().parents[2]

# Upper bounds after L2 mcp_config scope fix (2025-10-25).
_MAX_FINDINGS = {
    "secmcp": 25,
    "vendor/mcp-guard": 3,
    "prompts-directory-main": 5,
}


def test_fp_review_sample_trees_within_bounds() -> None:
    for rel, limit in _MAX_FINDINGS.items():
        root = REPO_ROOT / rel
        if not root.is_dir():
            continue
        result = scan_repository_sync(root)
        count = int(result["count"])
        assert count <= limit, (
            f"{rel}: {count} findings (max {limit}); "
            f"rules={sorted({f.get('rule') for f in result['findings']})}"
        )
