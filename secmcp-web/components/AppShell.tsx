import Link from "next/link";
import type { ReactNode } from "react";

import { UserMenu } from "@/components/UserMenu";

type AppShellProps = {
  children: ReactNode;
  active?: "dashboard";
};

export function AppShell({ children, active }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[#0B1220]">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-4">
          <Link href="/" className="text-sm font-semibold tracking-wide text-teal-500">
            SecMCP
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <Link
              href="/dashboard"
              className={
                active === "dashboard"
                  ? "text-white"
                  : "text-slate-400 hover:text-slate-200"
              }
            >
              Dashboard
            </Link>
            <Link href="/" className="text-slate-400 hover:text-slate-200">
              Home
            </Link>
            <UserMenu />
          </nav>
        </div>
      </header>
      {children}
    </div>
  );
}
