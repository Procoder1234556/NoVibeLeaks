import path from "path";

/** Monorepo root (parent of secmcp-web). Override with SECMCP_REPO_ROOT. */
export function repoRoot(): string {
  return process.env.SECMCP_REPO_ROOT ?? path.resolve(process.cwd(), "..");
}

export function pythonExecutable(): string {
  return process.env.SECMCP_PYTHON ?? "python";
}
