import Link from "next/link";

const MCP_SNIPPET = `{
  "mcpServers": {
    "secmcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/secmcp", "python", "server.py"]
    }
  }
}`;

const STEPS = [
  {
    title: "Add MCP",
    body: "Point Cursor or Claude Code at the SecMCP server — five security tools on every session.",
  },
  {
    title: "Scan",
    body: "Paste a snippet in the dashboard or run the GitHub Action on your repo.",
  },
  {
    title: "Fix",
    body: "Plain-English findings with file:line and actionable recommendations — no leaked secrets.",
  },
];

export function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0B1220] text-slate-100">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <span className="text-sm font-semibold tracking-wide text-teal-500">SecMCP</span>
          <nav className="flex gap-4 text-sm">
            <Link href="/dashboard" className="text-teal-400 hover:text-teal-300">
              Open dashboard
            </Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-16">
        <section className="mb-20">
          <h1 className="mb-4 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
            Security MCP for vibe-coded apps
          </h1>
          <p className="mb-8 max-w-2xl text-lg text-slate-400">
            Hardcoded secrets, API key checks, and LLM anti-patterns — in the IDE and in CI.
            Same Python scanner behind the MCP server and this dashboard.
          </p>
          <Link
            href="/dashboard"
            className="inline-flex rounded-lg bg-teal-700 px-6 py-3 text-sm font-semibold text-white hover:bg-teal-600"
          >
            Run a free snippet scan
          </Link>
        </section>

        <section className="mb-20 grid gap-6 sm:grid-cols-3">
          {STEPS.map((step, i) => (
            <div
              key={step.title}
              className="rounded-xl border border-slate-800 bg-slate-900/40 p-6"
            >
              <p className="mb-2 text-xs font-medium uppercase tracking-wider text-teal-500">
                Step {i + 1}
              </p>
              <h2 className="mb-2 text-lg font-medium text-white">{step.title}</h2>
              <p className="text-sm text-slate-400">{step.body}</p>
            </div>
          ))}
        </section>

        <section className="mb-12">
          <h2 className="mb-3 text-lg font-medium text-white">Cursor MCP config</h2>
          <pre
            className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 font-mono text-sm text-slate-300"
          >
            {MCP_SNIPPET}
          </pre>
          <p className="mt-3 text-sm text-slate-500">
            See the repo{" "}
            <code className="text-slate-400">.cursor/mcp.json.example</code> and{" "}
            <code className="text-slate-400">secmcp/README.md</code> for install steps.
          </p>
        </section>

        <section className="flex flex-wrap gap-4 text-sm text-slate-400">
          <a
            href="https://skills.sh/"
            className="text-teal-400 hover:text-teal-300"
            rel="noopener noreferrer"
            target="_blank"
          >
            Agent skills on skills.sh
          </a>
          <span aria-hidden="true">·</span>
          <span>Daily repo scans via GitHub Actions</span>
        </section>
      </main>
    </div>
  );
}
