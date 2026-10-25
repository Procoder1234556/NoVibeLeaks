export type ScanFinding = {
  rule: string;
  severity: string;
  category?: string;
  message?: string;
  recommendation?: string;
  location: { file: string; line: number; column?: number };
};

export type BreakdownBucket = {
  score: number;
  finding_count: number;
  findings: ScanFinding[];
};

export type ScanResult = {
  id?: string;
  source_label: string;
  overall_score: number;
  grade: string;
  summary: string;
  finding_count: number;
  breakdown: Record<string, BreakdownBucket>;
  persisted?: boolean;
  rules_load_warnings?: string[];
};

export type ScanHistoryRow = {
  id: string;
  created_at: string;
  source_label: string;
  overall_score: number;
  grade: string;
  finding_count: number;
};
