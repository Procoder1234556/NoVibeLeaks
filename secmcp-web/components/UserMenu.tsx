"use client";

import { useCallback, useEffect, useState } from "react";
import type { User } from "@supabase/supabase-js";

import { createClient } from "@/lib/supabase/client";
import { isSupabaseConfigured } from "@/lib/supabase/config";

export function UserMenu() {
  const [user, setUser] = useState<User | null>(null);
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [panelOpen, setPanelOpen] = useState(false);

  const refreshUser = useCallback(async () => {
    if (!isSupabaseConfigured()) return;
    const supabase = createClient();
    const { data } = await supabase.auth.getUser();
    setUser(data.user);
  }, []);

  useEffect(() => {
    if (!isSupabaseConfigured()) return;
    const supabase = createClient();
    refreshUser();
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(() => {
      refreshUser();
    });
    return () => subscription.unsubscribe();
  }, [refreshUser]);

  if (!isSupabaseConfigured()) {
    return (
      <span className="text-xs text-slate-500" title="Set NEXT_PUBLIC_SUPABASE_* in .env.local">
        Local mode (no auth)
      </span>
    );
  }

  const label =
    user?.email ??
    (user?.is_anonymous ? "Guest session" : user ? "Signed in" : "…");

  async function signInAnonymously() {
    setBusy(true);
    setMessage(null);
    try {
      const supabase = createClient();
      await supabase.auth.signInAnonymously();
      setPanelOpen(false);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Sign-in failed");
    } finally {
      setBusy(false);
    }
  }

  async function sendMagicLink() {
    const trimmed = email.trim();
    if (!trimmed) return;
    setBusy(true);
    setMessage(null);
    try {
      const supabase = createClient();
      const { error } = await supabase.auth.signInWithOtp({
        email: trimmed,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback?next=/dashboard`,
        },
      });
      if (error) throw error;
      setMessage("Check your email for the sign-in link.");
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Email sign-in failed");
    } finally {
      setBusy(false);
    }
  }

  async function signInWithGitHub() {
    setBusy(true);
    setMessage(null);
    try {
      const supabase = createClient();
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "github",
        options: {
          redirectTo: `${window.location.origin}/auth/callback?next=/dashboard`,
        },
      });
      if (error) throw error;
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "GitHub sign-in failed");
      setBusy(false);
    }
  }

  async function signOut() {
    setBusy(true);
    try {
      const supabase = createClient();
      await supabase.auth.signOut();
      await supabase.auth.signInAnonymously();
      setPanelOpen(false);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="relative">
      <button
        type="button"
        className="rounded-lg border border-slate-700 px-3 py-1.5 text-sm text-slate-200 hover:border-slate-500"
        onClick={() => setPanelOpen((v) => !v)}
        aria-expanded={panelOpen}
      >
        {label}
      </button>
      {panelOpen && (
        <div
          className="absolute right-0 z-20 mt-2 w-72 rounded-lg border border-slate-700 bg-slate-900 p-4 shadow-xl"
          role="dialog"
          aria-label="Account"
        >
          <p className="mb-3 text-xs text-slate-400">
            Email or GitHub keeps scan history across devices. Guest sessions work
            without linking.
          </p>
          <label className="mb-1 block text-xs text-slate-500" htmlFor="auth-email">
            Email magic link
          </label>
          <input
            id="auth-email"
            type="email"
            autoComplete="email"
            className="mb-2 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1.5 text-sm text-white"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
          />
          <button
            type="button"
            disabled={busy}
            onClick={sendMagicLink}
            className="mb-2 w-full rounded bg-teal-800 py-1.5 text-sm text-white hover:bg-teal-700 disabled:opacity-50"
          >
            Send link
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={signInWithGitHub}
            className="mb-2 w-full rounded border border-slate-600 py-1.5 text-sm text-slate-200 hover:bg-slate-800 disabled:opacity-50"
          >
            Continue with GitHub
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={signInAnonymously}
            className="mb-2 w-full text-xs text-teal-400 hover:text-teal-300"
          >
            Use guest session
          </button>
          {user && (
            <button
              type="button"
              disabled={busy}
              onClick={signOut}
              className="w-full text-xs text-slate-500 hover:text-slate-300"
            >
              Sign out
            </button>
          )}
          {message && <p className="mt-2 text-xs text-slate-400">{message}</p>}
        </div>
      )}
    </div>
  );
}
