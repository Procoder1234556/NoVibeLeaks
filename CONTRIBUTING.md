# Contributing to NoVibeLeaks

Thanks for helping keep vibe-coded apps from leaking secrets.

## Development setup

```bash
cd secmcp
uv sync
pytest -q
```

## Pull requests

1. Fork `Procoder1234556/NoVibeLeaks` and branch from `main`.
2. Add **pytest** for behavior changes under `secmcp/tests/`.
3. Keep the MCP surface to **five tools** unless the project RFC/PRD changes.
4. Run `python scripts/scan_repository.py --no-fail .` after touching `secmcp/` or `scripts/`.
5. Open a PR with a clear summary and test plan.

## YAML rules

Add rules as declarative `*.yaml` under `secmcp/rules/`. No executable code in rule files.

## Security

Report vulnerabilities via [GitHub Security Advisories](https://github.com/Procoder1234556/NoVibeLeaks/security/advisories/new) (private) before public disclosure.
