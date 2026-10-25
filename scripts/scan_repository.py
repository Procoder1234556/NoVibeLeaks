#!/usr/bin/env python3
"""Walk a repository and run SecMCP scans (Phase 2 GitHub Action entry)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from secmcp.reporting import write_sarif_file, write_vulnerabilities_txt_file
from secmcp.scanner import scan_repository_sync

_FAIL_SEVERITIES = frozenset({"critical", "high"})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SecMCP repository scan")
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Repository root or single file (default: .)",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON summary to stdout")
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Exit 0 even when critical/high findings exist (for scheduled CI)",
    )
    parser.add_argument(
        "--sarif",
        metavar="PATH",
        help="Write SARIF 2.1.0 report (GitHub Code Scanning)",
    )
    parser.add_argument(
        "--vulnerabilities",
        metavar="PATH",
        nargs="?",
        const="vulnerabilities.txt",
        help="Write plain-text findings report (default: vulnerabilities.txt in repo root)",
    )
    args = parser.parse_args(argv)

    try:
        result = scan_repository_sync(Path(args.root))
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 2

    if args.sarif:
        write_sarif_file(result, Path(args.sarif))

    if args.vulnerabilities is not None:
        vuln_path = Path(args.vulnerabilities)
        if args.vulnerabilities == "vulnerabilities.txt":
            vuln_path = Path(result.get("root", args.root)) / "vulnerabilities.txt"
        written = write_vulnerabilities_txt_file(result, vuln_path)
        if not args.json:
            print(f"Wrote {written}")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"Scanned {result['files_scanned']} files "
            f"({result['files_skipped']} skipped), {result['count']} findings"
        )
        for finding in result["findings"]:
            loc = finding.get("location", {})
            print(
                f"  [{finding.get('severity')}] {finding.get('rule')} "
                f"{loc.get('file')}:{loc.get('line')}"
            )

    if args.no_fail:
        return 0
    blocking = sum(
        result["severity_counts"].get(sev, 0) for sev in _FAIL_SEVERITIES
    )
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
