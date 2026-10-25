#!/usr/bin/env bash
# Publish NoVibeLeaks to PyPI + MCP Registry (maintainer).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/secmcp"
python -m pip install -q build twine
python -m build
python -m twine upload dist/*
cd "$ROOT"
npx --yes mcp-publisher@0.4.2 publish ./server.json
echo "Done. Search registry for io.github.Procoder1234556/novibeleaks"
