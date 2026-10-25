#!/usr/bin/env python3
"""stdin JSON → SecMCP security score JSON (Phase 3 web subprocess)."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from secmcp.scanner import security_score_async
from secmcp.web_payload import build_web_scan_result, validate_upload_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan a code snippet for the SecMCP web API")
    parser.add_argument(
        "--stdin-json",
        action="store_true",
        help="Read {\"code\": \"...\", \"label\": \"file.py\"} from stdin",
    )
    args = parser.parse_args(argv)

    if not args.stdin_json:
        print("Use --stdin-json", file=sys.stderr)
        return 2

    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 2

    code = str(payload.get("code") or "")
    label = str(payload.get("label") or "upload.txt")
    try:
        validate_upload_code(code)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    try:
        scored = asyncio.run(
            security_score_async(code=code, path=label, validate_keys=False)
        )
    except Exception as exc:  # noqa: BLE001 — surface to Node caller
        print(str(exc), file=sys.stderr)
        return 1

    result = build_web_scan_result(scored, source_label=label)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
