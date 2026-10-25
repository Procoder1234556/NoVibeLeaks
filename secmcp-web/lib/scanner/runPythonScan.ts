import { spawn } from "child_process";
import path from "path";

import { pythonExecutable, repoRoot } from "@/lib/repo";
import type { ScanResult } from "@/lib/types";

type PythonScanPayload = {
  source_label: string;
  overall_score: number;
  grade: string;
  summary: string;
  finding_count: number;
  breakdown: ScanResult["breakdown"];
  storage_breakdown: Record<string, { score: number; finding_count: number }>;
  rules_load_warnings: string[];
};

export async function runPythonScan(
  code: string,
  label: string,
): Promise<PythonScanPayload> {
  const root = repoRoot();
  const script = path.join(root, "scripts", "scan_snippet.py");
  const pythonPath = path.join(root, "secmcp");

  return new Promise((resolve, reject) => {
    const proc = spawn(
      pythonExecutable(),
      [script, "--stdin-json"],
      {
        cwd: pythonPath,
        env: { ...process.env, PYTHONPATH: pythonPath },
        stdio: ["pipe", "pipe", "pipe"],
      },
    );

    let stdout = "";
    let stderr = "";
    proc.stdout.on("data", (chunk: Buffer) => {
      stdout += chunk.toString();
    });
    proc.stderr.on("data", (chunk: Buffer) => {
      stderr += chunk.toString();
    });
    proc.on("error", (err) => reject(err));
    proc.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(stderr.trim() || `Scanner exited with code ${code}`));
        return;
      }
      try {
        resolve(JSON.parse(stdout) as PythonScanPayload);
      } catch {
        reject(new Error("Invalid JSON from scanner"));
      }
    });

    proc.stdin.write(JSON.stringify({ code, label }));
    proc.stdin.end();
  });
}
