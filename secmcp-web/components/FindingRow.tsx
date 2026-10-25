"use client";

import { useState } from "react";

import { SeverityBadge } from "@/components/SeverityBadge";
import type { ScanFinding } from "@/lib/types";

export function FindingRow({ finding }: { finding: ScanFinding }) {
  const [open, setOpen] = useState(false);
  const hasRec = Boolean(finding.recommendation?.trim());

  return (
    <tr className="border-t border-slate-800">
      <td className="px-4 py-2">
        <SeverityBadge severity={finding.severity} />
      </td>
      <td className="px-4 py-2 text-slate-200">{finding.message}</td>
      <td className="px-4 py-2 font-mono text-xs text-slate-400">
        {finding.location.file}:{finding.location.line}
      </td>
      <td className="px-4 py-2">
        {hasRec ? (
          <button
            type="button"
            className="text-xs text-teal-400 hover:text-teal-300 focus:outline-none focus:ring-2 focus:ring-teal-600 rounded"
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                setOpen((v) => !v);
              }
            }}
          >
            {open ? "Hide fix" : "Show fix"}
          </button>
        ) : (
          <span className="text-xs text-slate-600">—</span>
        )}
        {open && hasRec && (
          <p className="mt-2 max-w-md text-xs text-slate-400">{finding.recommendation}</p>
        )}
      </td>
    </tr>
  );
}
