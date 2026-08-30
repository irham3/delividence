"use client";

import { useCallback, useState, type ReactNode } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  CheckCircle2,
  ClipboardList,
  FileStack,
  HelpCircle,
  Inbox,
  Layers3,
  LogOut,
  Plus,
  ListChecks,
  Search,
  Settings,
  Activity,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { ConfirmDialog } from "@/components/delividence/confirm-dialog";

type AppShellProps = {
  email?: string | null;
  onSignOut: () => void | Promise<void>;
  onNewRecord: () => void;
  children: ReactNode;
  rightRail?: ReactNode;
};

const navItems: Array<[string, string, LucideIcon]> = [
  ["Workspace", "/workspace", Inbox],
  ["Records", "/records", FileStack],
  ["Sources", "/sources", Layers3],
  ["Review", "/review", ListChecks],
  ["Activity", "/activity", Activity],
];

export function AppShell({ email, onSignOut, onNewRecord, children, rightRail }: AppShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [confirmingSignOut, setConfirmingSignOut] = useState(false);
  const [signingOut, setSigningOut] = useState(false);
  const [signOutError, setSignOutError] = useState<string | null>(null);
  const cancelSignOut = useCallback(() => {
    if (!signingOut) setConfirmingSignOut(false);
  }, [signingOut]);

  async function confirmSignOut() {
    setSignOutError(null);
    setSigningOut(true);
    try {
      await onSignOut();
      setConfirmingSignOut(false);
    } catch (cause) {
      setSignOutError(cause instanceof Error ? cause.message : "Sign out failed. Please try again.");
    } finally {
      setSigningOut(false);
    }
  }

  return (
    <div className="paper-texture min-h-[100dvh]">
      <div className="grid min-h-[100dvh] lg:grid-cols-[224px_1fr]">
        <aside className="hidden border-r border-[var(--rule)] surface-o72 px-5 py-6 backdrop-blur-xl lg:block">
          <div className="flex items-center gap-2 text-lg font-semibold tracking-tight"><Image src="/assets/delividence-mark.svg" alt="" aria-hidden="true" width={24} height={24} />Delividence</div>
          <nav className="mt-10 space-y-1">
            {navItems.map(([label, href, Icon]) => {
              const active = pathname === href || (href === "/workspace" && pathname === "/") || (href === "/records" && pathname.startsWith("/records"));
              return (
              <Link
                key={label}
                href={href}
                className={`focus-ring tap flex w-full items-center gap-3 rounded-[6px] px-3 py-2.5 text-left text-sm ${
                  active
                    ? "bg-[var(--accent-soft)] text-[var(--ink)]"
                    : "text-[var(--muted)] surface-hover-o60 hover:text-[var(--ink)]"
                }`}
              >
                <Icon size={17} strokeWidth={1.8} />
                {label}
              </Link>
            )})}
          </nav>
          <div className="mt-12 border-t border-[var(--rule)] pt-5">
            <Link href="/settings/policies" className="focus-ring tap flex w-full items-center gap-3 rounded-[6px] px-3 py-2.5 text-left text-sm text-[var(--muted)] surface-hover-o60 hover:text-[var(--ink)]">
              <Settings size={17} strokeWidth={1.8} />
              Policies
            </Link>
            <a href="mailto:hello@delividence.com?subject=Delividence%20help" className="focus-ring tap flex w-full items-center gap-3 rounded-[6px] px-3 py-2.5 text-left text-sm text-[var(--muted)] surface-hover-o60 hover:text-[var(--ink)]">
              <HelpCircle size={17} strokeWidth={1.8} />
              Help
            </a>
          </div>
        </aside>

        <div>
          <header className="sticky top-0 z-20 border-b border-[var(--rule)] canvas-o88 backdrop-blur-xl">
            <div className="flex h-16 items-center justify-between gap-4 px-5 sm:px-8">
              <div className="flex min-w-0 flex-1 items-center gap-3">
                <div className="flex items-center gap-2 text-lg font-semibold tracking-tight lg:hidden"><Image src="/assets/delividence-mark.svg" alt="" aria-hidden="true" width={24} height={24} />Delividence</div>
                <form
                  role="search"
                  className="focus-within:ring-2 focus-within:ring-[var(--accent)]/45 hidden min-w-80 items-center gap-2 rounded-[6px] border border-[var(--rule)] surface-o60 px-3 py-2 sm:flex"
                  onSubmit={(event) => {
                    event.preventDefault();
                    const query = new FormData(event.currentTarget).get("q")?.toString().trim() ?? "";
                    router.push(query ? `/records?q=${encodeURIComponent(query)}` : "/records");
                  }}
                >
                  <Search size={16} strokeWidth={1.8} className="text-[var(--muted)]" />
                  <label htmlFor="record-search" className="sr-only">Search records</label>
                  <input
                    id="record-search"
                    name="q"
                    className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-[var(--faint)]"
                    placeholder="Search records"
                  />
                </form>
              </div>
              <button
                className="tap focus-ring inline-flex items-center gap-2 rounded-[6px] bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--accent-dark)]"
                onClick={() => {
                  onNewRecord();
                  if (pathname !== "/workspace" && pathname !== "/") router.push("/records/new");
                }}
              >
                <Plus size={16} strokeWidth={1.9} />
                New record
              </button>
              <button onClick={() => setConfirmingSignOut(true)} aria-label="Sign out" title="Sign out" className="focus-ring tap surface-o60 inline-flex rounded-[6px] border border-[var(--rule)] p-2 text-[var(--muted)] md:hidden">
                <LogOut size={17} strokeWidth={1.8} />
              </button>
              <div className="hidden min-w-0 text-right md:block">
                <p className="truncate text-sm font-medium">{email ?? "Signed in"}</p>
                <button onClick={() => setConfirmingSignOut(true)} className="focus-ring tap inline-flex items-center gap-1 text-xs text-[var(--muted)] hover:text-[var(--ink)]">
                  <LogOut size={13} strokeWidth={1.8} />
                  Sign out
                </button>
              </div>
            </div>
            <nav aria-label="Workspace navigation" className="editorial-scroll flex gap-1 overflow-x-auto border-t border-[var(--rule)] px-4 py-2 lg:hidden">
              {navItems.map(([label, href, Icon]) => {
                const active = pathname === href || (href === "/workspace" && pathname === "/") || (href === "/records" && pathname.startsWith("/records"));
                return (
                  <Link key={label} href={href} className={`focus-ring tap inline-flex shrink-0 items-center gap-2 rounded-[6px] px-3 py-2 text-xs ${active ? "bg-[var(--accent-soft)] text-[var(--ink)]" : "text-[var(--muted)]"}`}>
                    <Icon size={15} strokeWidth={1.8} />
                    {label}
                  </Link>
                );
              })}
            </nav>
          </header>

          <main className="grid gap-8 px-5 py-8 sm:px-8 xl:grid-cols-[minmax(0,1fr)_340px]">
            <div>{children}</div>
            {rightRail && <aside className="space-y-5">{rightRail}</aside>}
          </main>
        </div>
      </div>
      <ConfirmDialog
        open={confirmingSignOut}
        title="Sign out of Delividence?"
        description="Your saved records stay intact. You will need to choose your Google account again to continue."
        confirmLabel="Sign out"
        busyLabel="Signing out..."
        busy={signingOut}
        error={signOutError}
        destructive
        onCancel={cancelSignOut}
        onConfirm={() => void confirmSignOut()}
      />
    </div>
  );
}

export function WorkspaceHeader({ status, runId }: { status?: string; runId?: string | null }) {
  return (
    <div className="mb-8 flex flex-col justify-between gap-4 border-b border-[var(--rule)] pb-7 lg:flex-row lg:items-end">
      <div>
        <p className="mono text-xs uppercase tracking-[0.12em] text-[var(--muted)]">Workspace</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">Good morning. Here&apos;s what&apos;s next.</h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-[var(--muted)]">
          Keep the brief, the decision, and the proof in one working record.
        </p>
      </div>
      <div className="paper-card min-w-64 rounded-[8px] p-4">
        <p className="text-sm text-[var(--muted)]">Current run</p>
        <p className="mt-2 mono truncate text-xs">{runId ?? "No active run"}</p>
        <div className="mt-4 flex items-center gap-2 text-sm">
          <CheckCircle2 size={17} strokeWidth={1.8} className="text-[var(--accepted)]" />
          <span>{status ?? "Ready"}</span>
        </div>
      </div>
    </div>
  );
}

export function RailPanel({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="paper-card rounded-[8px] p-5">
      <div className="flex items-center gap-2">
        <ClipboardList size={17} strokeWidth={1.8} className="text-[var(--accent)]" />
        <h2 className="font-semibold tracking-tight">{title}</h2>
      </div>
      <div className="mt-5">{children}</div>
    </section>
  );
}
