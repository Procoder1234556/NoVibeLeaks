import { NextResponse } from "next/server";

import { createClient } from "@/lib/supabase/server";
import { isSupabaseConfigured } from "@/lib/supabase/config";
import type { ScanHistoryRow } from "@/lib/types";

export async function GET() {
  if (!isSupabaseConfigured()) {
    return NextResponse.json({ scans: [] as ScanHistoryRow[] });
  }

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ scans: [] as ScanHistoryRow[] });
  }

  const { data, error } = await supabase
    .from("scans")
    .select("id, created_at, source_label, overall_score, grade, finding_count")
    .eq("user_id", user.id)
    .order("created_at", { ascending: false })
    .limit(25);

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ scans: data ?? [] });
}
