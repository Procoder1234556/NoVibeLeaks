import { NextResponse } from "next/server";

import { runPythonScan } from "@/lib/scanner/runPythonScan";
import { createClient } from "@/lib/supabase/server";
import { isSupabaseConfigured } from "@/lib/supabase/config";
import type { ScanResult } from "@/lib/types";

const MAX_LABEL_LEN = 200;

export async function POST(request: Request) {
  let body: { code?: string; label?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const code = typeof body.code === "string" ? body.code : "";
  const label =
    typeof body.label === "string" && body.label.trim()
      ? body.label.trim().slice(0, MAX_LABEL_LEN)
      : "upload.txt";

  if (!code.trim()) {
    return NextResponse.json({ error: "Code snippet is required" }, { status: 400 });
  }

  try {
    const scanned = await runPythonScan(code, label);
    const response: ScanResult = {
      source_label: scanned.source_label,
      overall_score: scanned.overall_score,
      grade: scanned.grade,
      summary: scanned.summary,
      finding_count: scanned.finding_count,
      breakdown: scanned.breakdown,
      rules_load_warnings: scanned.rules_load_warnings,
      persisted: false,
    };

    if (isSupabaseConfigured()) {
      const supabase = await createClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (user) {
        const { data, error } = await supabase
          .from("scans")
          .insert({
            user_id: user.id,
            source_type: "upload",
            source_label: scanned.source_label,
            overall_score: scanned.overall_score,
            grade: scanned.grade,
            breakdown: scanned.storage_breakdown,
            finding_count: scanned.finding_count,
          })
          .select("id")
          .single();

        if (!error && data?.id) {
          response.id = data.id;
          response.persisted = true;
        }
      }
    }

    return NextResponse.json(response);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Scan failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
