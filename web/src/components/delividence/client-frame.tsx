"use client";

import type { ReactNode } from "react";
import { LockKeyhole } from "lucide-react";
import { ThemeToggle } from "@/components/delividence/theme-toggle";

export function ClientFrame({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: ReactNode;
}) {
  return (
    <main className="paper-texture min-h-[100dvh] px-5 py-8 sm:px-8">
      <div className="mx-auto max-w-5xl">
        <header className="mb-8 flex flex-col justify-between gap-4 border-b border-[var(--rule)] pb-6 sm:flex-row sm:items-center">
          <div>
            <p className="text-lg font-semibold tracking-tight">Delividence</p>
            <h1 className="mt-6 text-4xl font-semibold tracking-tight">{title}</h1>
            {description && <p className="mt-4 max-w-2xl text-base leading-7 text-[var(--muted)]">{description}</p>}
          </div>
          <div className="flex items-center gap-3">
            <div className="inline-flex w-fit items-center gap-2 rounded-[6px] border border-[var(--rule)] surface-o60 px-3 py-2 text-sm text-[var(--muted)]">
              <LockKeyhole size={16} strokeWidth={1.8} />
              Secure client link
            </div>
            <ThemeToggle />
          </div>
        </header>
        {children}
      </div>
    </main>
  );
}

export function ClientCard({ children }: { children: ReactNode }) {
  return <section className="paper-card record-shadow rounded-[8px] p-5 sm:p-6">{children}</section>;
}
