"use client";

import { useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { onAuthStateChanged, type User } from "firebase/auth";
import { ArrowLeft, LockKeyhole } from "lucide-react";
import { AppShell } from "@/components/delividence/app-shell";
import { getFirebaseAuth, signInWithGoogle, signOutOwner } from "@/lib/firebase";
import { setAuthTokenProvider } from "@/lib/api";

setAuthTokenProvider(() => {
  try {
    const auth = getFirebaseAuth();
    return auth.currentUser ? auth.currentUser.getIdToken() : Promise.resolve(null);
  } catch {
    return Promise.resolve(null);
  }
});

export function OwnerGate({ children }: { children: (user: User) => ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let unsubscribe: () => void = () => {};
    let failureTimer: number | undefined;
    try {
      const auth = getFirebaseAuth();
      unsubscribe = onAuthStateChanged(auth, (next) => {
        setUser(next);
        setReady(true);
      });
    } catch (cause) {
      // Defer the configuration failure to the next task. React's hook lint
      // correctly rejects a synchronous state update inside an effect body.
      failureTimer = window.setTimeout(() => {
        setError(cause instanceof Error ? cause.message : "Firebase is not configured.");
        setReady(true);
      }, 0);
    }
    return () => {
      unsubscribe();
      if (failureTimer) window.clearTimeout(failureTimer);
    };
  }, []);

  if (!ready) {
    return <main className="paper-texture flex min-h-[100dvh] items-center justify-center px-5"><p className="text-sm text-[var(--muted)]">Loading Delividence...</p></main>;
  }

  if (!user) {
    return <OwnerSignIn error={error} onSignIn={() => signInWithGoogle().catch((e) => setError(e instanceof Error ? e.message : "Sign-in failed."))} />;
  }

  return (
    <AppShell
      email={user.email}
      onSignOut={() => signOutOwner()}
      onNewRecord={() => undefined}
    >
      {children(user)}
    </AppShell>
  );
}

export function OwnerSignIn({ error, onSignIn, register = false }: { error?: string | null; onSignIn: () => void; register?: boolean }) {
  return (
    <main className="paper-texture grid min-h-[100dvh] grid-rows-[72px_1fr_auto] px-5 sm:px-8">
      <header className="mx-auto flex w-full max-w-[1344px] items-center justify-between border-b border-[var(--rule)]">
        <Link href="/" className="focus-ring text-lg font-semibold tracking-tight">Delividence</Link>
        <Link href="/" className="focus-ring inline-flex items-center gap-2 text-sm text-[var(--muted)]"><ArrowLeft size={15} /> Home</Link>
      </header>
      <section className="mx-auto flex w-full max-w-md items-center py-16">
        <div className="paper-card record-shadow w-full rounded-[8px] p-7 sm:p-9">
          <p className="mono text-[11px] font-medium tracking-[0.1em] text-[var(--accent)]">{register ? "START A RECORD" : "WELCOME BACK"}</p>
          <h1 className="mt-5 text-4xl font-semibold tracking-tight">{register ? "Make the next decision easier." : "Continue the record."}</h1>
          <p className="mt-4 max-w-sm text-sm leading-6 text-[var(--muted)]">{register ? "Create a workspace for material, agreement, and proof." : "Sign in to the work you are keeping clear."}</p>
          <button onClick={onSignIn} className="tap focus-ring mt-8 flex min-h-12 w-full items-center justify-center gap-3 rounded-[4px] border border-[var(--ink)] bg-[var(--surface-strong)] text-sm font-medium">
            <span className="grid h-5 w-5 place-items-center font-semibold text-[#4285f4]" aria-hidden="true">G</span>
            {register ? "Sign up with Google" : "Continue with Google"}
          </button>
          <p className="mt-6 text-center text-sm text-[var(--muted)]">{register ? <>Already have an account? <Link href="/sign-in" className="focus-ring text-[var(--ink)] underline">Sign in.</Link></> : <>New to Delividence? <Link href="/register" className="focus-ring text-[var(--ink)] underline">Create an account.</Link></>}</p>
          {register && <p className="mt-5 text-center text-xs leading-5 text-[var(--muted)]">By continuing, you agree to the Terms and Privacy Policy.</p>}
          {error && <p className="mt-5 border border-[var(--danger)]/30 p-3 text-sm text-[var(--danger)]">{error}</p>}
        </div>
      </section>
      <footer className="mx-auto flex w-full max-w-[1344px] flex-wrap items-center justify-between gap-4 border-t border-[var(--rule)] py-6 text-xs text-[var(--muted)]"><span className="inline-flex items-center gap-2"><LockKeyhole size={14} /> Your record stays yours.</span><span>Privacy · Security · Help Center</span></footer>
    </main>
  );
}
