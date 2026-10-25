# SecMCP Web (Phase 3)

Next.js 15 dashboard: paste code → Python `secmcp` scanner → score + optional Supabase history.

## Prerequisites

- Node 20+
- Python 3.11+ with `secmcp` on `PYTHONPATH` (repo layout: `../secmcp` + `../scripts/scan_snippet.py`)
- Optional: [Supabase](https://supabase.com) project with **Anonymous sign-ins** enabled (Auth → Providers)

## Setup

```bash
cp .env.example .env.local
# Apply supabase/migrations/20251025000000_scans.sql in the SQL editor
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) (marketing) or [/dashboard](http://localhost:3000/dashboard) (scanner).

### Auth (optional)

Enable **Anonymous**, **Email**, and/or **GitHub** in Supabase Auth → Providers. Set redirect URL to `http://localhost:3000/auth/callback` (and your production URL). The dashboard uses guest sessions by default; use the user menu for magic link or GitHub.

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/scan` | JSON `{ "code": "...", "label": "file.py" }` |
| GET | `/api/scans` | Recent scans for the signed-in user |

Scanner subprocess: `scripts/scan_snippet.py --stdin-json` (2MB cap, no `validate_keys` on upload).

## Tests

```bash
npm run test:e2e   # Playwright: landing + dashboard scan (needs Python secmcp on PATH / SECMCP_REPO_ROOT)
```

CI: `.github/workflows/secmcp-web-ci.yml`.

## Deploy

Vercel + set `NEXT_PUBLIC_SUPABASE_*`, `SECMCP_REPO_ROOT` (monorepo root on the build image), and install `pip install -e secmcp` in a build step if the scanner subprocess is required in production.
