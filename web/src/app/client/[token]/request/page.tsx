"use client";

import { use, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

type NewRequestView = { brief: string };

export default function NewRequestPage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = use(params);

  const [view, setView] = useState<NewRequestView | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [rawText, setRawText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submittedCount, setSubmittedCount] = useState(0);

  async function load() {
    try {
      const v = await apiFetch<NewRequestView>(`/client/${token}/new-request`);
      setView(v);
      setLoadError(null);
    } catch (e) {
      setLoadError(e instanceof Error ? e.message : "Failed to load this link.");
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setSubmitError(null);
    try {
      await apiFetch(`/client/${token}/new-request`, {
        method: "POST",
        body: JSON.stringify({ raw_text: rawText }),
      });
      setRawText("");
      setSubmittedCount((n) => n + 1);
    } catch (e) {
      setSubmitError(e instanceof Error ? e.message : "Failed to submit.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loadError) {
    return (
      <main className="mx-auto max-w-2xl px-6 py-16">
        <h1 className="text-xl font-semibold">This link isn&apos;t available</h1>
        <p className="mt-2 text-sm text-red-700">{loadError}</p>
      </main>
    );
  }

  if (!view) {
    return (
      <main className="mx-auto max-w-2xl px-6 py-16">
        <p className="text-sm text-neutral-500">Loading…</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <h1 className="text-2xl font-semibold tracking-tight">Ask for something new</h1>
      <p className="mt-2 text-sm text-neutral-500">
        Need something beyond what was originally agreed? Describe it below and your freelancer
        will review it against the confirmed plan.
      </p>
      <p className="mt-4 whitespace-pre-wrap rounded-md bg-neutral-50 p-3 text-sm text-neutral-700 dark:bg-neutral-900 dark:text-neutral-300">
        {view.brief}
      </p>

      <form onSubmit={submit} className="mt-8 space-y-4">
        <textarea
          value={rawText}
          onChange={(e) => setRawText(e.target.value)}
          required
          rows={5}
          placeholder="What would you like to ask for or add?"
          className="w-full rounded-md border border-neutral-300 p-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
        />
        <button
          type="submit"
          disabled={submitting || rawText.trim().length === 0}
          className="rounded-md bg-neutral-900 px-4 py-2 text-sm text-white disabled:opacity-40 dark:bg-white dark:text-neutral-900"
        >
          {submitting ? "Sending…" : "Send request"}
        </button>
      </form>
      {submitError && <p className="mt-3 text-sm text-red-700">{submitError}</p>}
      {submittedCount > 0 && (
        <p className="mt-3 text-sm text-green-800">
          Sent. Your freelancer will review it against the confirmed plan
          {submittedCount > 1 ? ` (${submittedCount} sent so far)` : ""}. You can send another one
          below if needed.
        </p>
      )}
    </main>
  );
}
