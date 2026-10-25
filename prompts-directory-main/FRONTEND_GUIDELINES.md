# Frontend Design System — SecMCP Dashboard (Phase 3)

**Status:** Implemented in `secmcp-web/` (landing + dashboard). Aligns with PRD Phase 3.

## 1. Design Principles

1. **Trust first** — security product; no playful gradients on severity alerts.
2. **Scannable scores** — five dimensions visible in &lt; 5 seconds.
3. **No secret display** — never render full matched tokens; show rule name + location only.

## 2. Brand

| Token | Value | Usage |
|-------|-------|--------|
| Name | SecMCP / VibeSec | Logo wordmark |
| Primary | `#0F766E` (teal 700) | CTAs, links |
| Critical | `#B91C1C` | Critical findings |
| High | `#C2410C` | High |
| Medium | `#CA8A04` | Medium |
| Low | `#64748B` | Low |
| Background | `#0B1220` / `#FFFFFF` | Dark default for dev audience; light mode optional |
| Font | `Inter`, system-ui | Body |
| Mono | `JetBrains Mono` | File paths, line numbers |

## 3. Layout

### Dashboard shell

- Top: logo, “New scan”, user menu
- Main: score hero (0–100) + grade letter
- Below: 4 cards — Secrets, API Keys, Configuration, Code Quality
- Table: findings (severity badge, message, file:line, recommendation expand)

### Landing (marketing)

- Hero: “Security MCP for vibe-coded apps”
- 3 steps: Add MCP → Scan → Fix
- Code block: Cursor `mcp.json` snippet
- Link to GitHub + skills.sh find-skills

## 4. Components

| Component | Behavior |
|-----------|----------|
| `ScoreRing` | Animated 0–100; color by grade |
| `SeverityBadge` | critical/high/medium/low — fixed colors |
| `FindingRow` | Truncate path; copy recommendation |
| `UploadZone` | Drag zip; max size TBD (e.g. 5MB MVP) |
| `HistoryList` | Date, overall score, delta vs previous |

## 5. Accessibility

- WCAG 2.1 AA contrast on badges
- Severity not color-only (icon + text)
- Keyboard: upload zone focusable; table row expand on Enter

## 6. Tech (when built)

- Next.js 15 App Router
- Tailwind CSS 4.x or 3.4+ (lock at scaffold time)
- shadcn/ui optional for Table, Badge, Card
- Supabase Auth UI or custom email magic link

## 7. Copy tone

- Plain English: “Hardcoded OpenAI API key detected” not “PATTERN_MATCH sk-*”
- Recommendations actionable: env var name, rotate link to provider docs

## 8. Out of scope UI

- Rule marketplace UI (P2)
- Real-time collaborative scan
- In-browser full repo IDE
