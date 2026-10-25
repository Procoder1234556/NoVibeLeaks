"use client";

import { useCallback, useEffect, useState } from "react";

import { FindingRow } from "@/components/FindingRow";
import { ScoreRing } from "@/components/ScoreRing";
import { createClient } from "@/lib/supabase/client";
import { isSupabaseConfigured } from "@/lib/supabase/config";
import type { BreakdownBucket, ScanHistoryRow, ScanResult } from "@/lib/types";

const CATEGORY_LABELS: Record<string, string> = {
  secrets: "Secrets",
  api_keys: "API Keys",
  configuration: "Configuration",
  code_quality: "Code Quality",
};

function historyDelta(
  row: ScanHistoryRow,
  index: number,
  rows: ScanHistoryRow[],
): string | null {
  const older = rows[index + 1];
  if (!older) return null;
  const delta = row.overall_score - older.overall_score;
  if (delta === 0) return "±0";
  return delta > 0 ? `+${delta}` : String(delta);
}

export function ScanDashboard() {
  const [code, setCode] = useState(
    'api_key = "sk-abcdefghijklmnopqrstuvwxyz123456"\n',
  );
  const [label, setLabel] = useState("snippet.py");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [history, setHistory] = useState<ScanHistoryRow[]>([]);
  const [authReady, setAuthReady] = useState(!isSupabaseConfigured());

  const refreshHistory = useCallback(async () => {
    const res = await fetch("/api/scans");
    if (!res.ok) return;
    const data = await res.json();
    setHistory(data.scans ?? []);
  }, []);

  useEffect(() => {
    if (!isSupabaseConfigured()) {
      return;
    }
    const supabase = createClient();
    supabase.auth.getSession().then(async ({ data }) => {
      if (!data.session) {
        await supabase.auth.signInAnonymously();
      }
      setAuthReady(true);
      await refreshHistory();
    });
  }, [refreshHistory]);

  async function onScan() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, label }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error ?? "Scan failed");
      }
      setResult(data as ScanResult);
      await refreshHistory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scan failed");
    } finally {
      setLoading(false);
    }
  }

  const buckets = result
    ? (Object.entries(result.breakdown) as [string, BreakdownBucket][])
    : [];

  return (
    <div
      className="mx-auto flex w-full max-w-5xl flex-col gap-10 px-4 py-10"
      data-testid="scan-dashboard"
    >
      <div className="flex flex-col gap-2 border-b border-slate-800 pb-6">
        <h1 className="text-3xl font-semibold text-white">New scan</h1>
        <p className="max-w-2xl text-slate-400">
          Paste code and run the same Python scanner as the MCP server. History
          syncs when Supabase auth is configured.
        </p>
      </div>

      <section className="grid gap-4 lg:grid-cols-[1fr_200px]">
        <div>
          <label className="mb-2 block text-sm text-slate-400" htmlFor="code">
            Code
          </label>
          <textarea
            id="code"
            data-testid="code-input"
            className="min-h-[200px] w-full rounded-lg border border-slate-700 bg-slate-950 p-3 font-mono text-sm text-slate-100 focus:border-teal-600 focus:outline-none"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            spellCheck={false}
          />
        </div>
        <div className="flex flex-col gap-3">
          <div>
            <label className="mb-2 block text-sm text-slate-400" htmlFor="label">
              Filename label
            </label>
            <input
              id="label"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
            />
          </div>
          <button
            type="button"
            data-testid="run-scan"
            onClick={onScan}
            disabled={loading || !authReady}
            className="mt-auto rounded-lg bg-teal-700 px-4 py-3 text-sm font-semibold text-white hover:bg-teal-600 disabled:opacity-50"
          >
            {loading ? "Scanning…" : "Run scan"}
          </button>
          {error && <p className="text-sm text-red-400">{error}</p>}
        </div>
      </section>

      {result && (
        <section className="flex flex-col gap-6" data-testid="scan-result">
          <div className="flex flex-wrap items-center gap-8 rounded-xl border border-slate-800 bg-slate-900/50 p-8">
            <ScoreRing score={result.overall_score} grade={result.grade} />
            <div className="flex-1 min-w-[200px]">
              <p className="text-sm text-slate-400">Summary</p>
              <p className="text-slate-200">{result.summary}</p>
              {result.persisted === false && isSupabaseConfigured() && (
                <p className="mt-2 text-xs text-amber-400">
                  Score not saved — sign in or check RLS policies.
                </p>
              )}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {buckets.map(([key, bucket]) => (
              <div
                key={key}
                className="rounded-lg border border-slate-800 bg-slate-950 p-4"
              >
                <p className="text-sm text-slate-400">
                  {CATEGORY_LABELS[key] ?? key}
                </p>
                <p className="text-3xl font-semibold text-white">
                  {bucket.score}
                </p>
                <p className="text-xs text-slate-500">
                  {bucket.finding_count} finding
                  {bucket.finding_count === 1 ? "" : "s"}
                </p>
              </div>
            ))}
          </div>

          {buckets.some(([, b]) => b.findings?.length) && (
            <div className="overflow-hidden rounded-lg border border-slate-800">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-900 text-slate-400">
                  <tr>
                    <th className="px-4 py-2">Severity</th>
                    <th className="px-4 py-2">Message</th>
                    <th className="px-4 py-2 font-mono">Location</th>
                    <th className="px-4 py-2">Fix</th>
                  </tr>
                </thead>
                <tbody>
                  {buckets.flatMap(([, bucket]) =>
                    bucket.findings.map((f, i) => (
                      <FindingRow key={`${f.rule}-${i}`} finding={f} />
                    )),
                  )}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      <section>
        <h2 className="mb-3 text-lg font-medium text-white">History</h2>
        {history.length === 0 ? (
          <p className="text-sm text-slate-500">
            No saved scans yet. Configure Supabase and enable anonymous sign-in
            to persist history.
          </p>
        ) : (
          <ul className="divide-y divide-slate-800 rounded-lg border border-slate-800">
            {history.map((row, index) => {
              const delta = historyDelta(row, index, history);
              return (
                <li
                  key={row.id}
                  className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm"
                >
                  <span className="font-mono text-slate-300">
                    {row.source_label}
                  </span>
                  <span className="text-slate-500">
                    {new Date(row.created_at).toLocaleString()}
                  </span>
                  <span className="font-semibold text-teal-400">
                    {row.overall_score} ({row.grade})
                    {delta && (
                      <span className="ml-2 text-xs font-normal text-slate-500">
                        {delta} vs prior
                      </span>
                    )}
                  </span>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}
