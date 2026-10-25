#!/usr/bin/env python3
"""Render GitHub issue title/body from a SecMCP scan JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from secmcp.reporting import format_github_issue


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render SecMCP daily scan GitHub issue")
    parser.add_argument("scan_json", type=Path, help="Path to scan-result.json")
    parser.add_argument("--ref", default="main", help="Git ref label for issue body")
    parser.add_argument("--sha", default="", help="Full commit SHA")
    parser.add_argument(
        "--docs-url",
        default="",
        help="README link (default: derive from GITHUB_REPOSITORY env)",
    )
    parser.add_argument("--title-out", type=Path, help="Write issue title to file")
    parser.add_argument("--body-out", type=Path, help="Write issue body to file")
    args = parser.parse_args(argv)

    if not args.scan_json.is_file():
        print(f"Missing scan JSON: {args.scan_json}", file=sys.stderr)
        return 2

    scan = json.loads(args.scan_json.read_text(encoding="utf-8"))
    docs_url = args.docs_url
    if not docs_url:
        import os

        repo = os.environ.get("GITHUB_REPOSITORY", "")
        docs_url = f"https://github.com/{repo}/blob/HEAD/secmcp/README.md" if repo else ""

    title, body = format_github_issue(scan, ref=args.ref, sha=args.sha, docs_url=docs_url)

    if args.title_out:
        args.title_out.write_text(title + "\n", encoding="utf-8")
    else:
        print(title)

    if args.body_out:
        args.body_out.write_text(body, encoding="utf-8")
    else:
        print(body)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
