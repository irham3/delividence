"use client";

import { use, useEffect, useState } from "react";
import { ClientCard, ClientFrame } from "@/components/delividence/client-frame";
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
      <ClientFrame title="This link is not available">
        <ClientCard>
          <p className="text-sm text-[var(--danger)]">{loadError}</p>
        </ClientCard>
      </ClientFrame>
    );
  }

  if (!view) {
    return (
      <ClientFrame title="Loading request page">
        <ClientCard>
          <p className="text-sm text-[var(--muted)]">Loading...</p>
        </ClientCard>
      </ClientFrame>
    );
  }

  return (
    <ClientFrame
      title="Ask for something new"
      description="New requests are captured separately, then reviewed against the confirmed plan."
    >
      <ClientCard>
      <p className="text-sm leading-6 text-[var(--muted)]">
        Need something beyond what was originally agreed? Describe it below and your freelancer
        will review it against the confirmed plan.
      </p>
      <p className="mt-4 whitespace-pre-wrap rounded-[6px] border border-[var(--rule)] bg-[var(--surface-strong)] p-4 text-sm leading-6 text-[var(--muted)]">
        {view.brief}
      </p>

      <form onSubmit={submit} className="mt-8 space-y-4">
        <textarea
          value={rawText}
          onChange={(e) => setRawText(e.target.value)}
          required
          rows={5}
          placeholder="What would you like to ask for or add?"
          className="focus-ring w-full rounded-[6px] border border-[var(--rule)] bg-[var(--surface-strong)] p-4 text-sm leading-6"
        />
        <button
          type="submit"
          disabled={submitting || rawText.trim().length === 0}
          className="tap focus-ring rounded-[6px] bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
        >
          {submitting ? "Sending..." : "Send request"}
        </button>
      </form>
      {submitError && <p className="mt-3 text-sm text-[var(--danger)]">{submitError}</p>}
      {submittedCount > 0 && (
        <p className="mt-3 text-sm text-[var(--accepted)]">
          Sent. Your freelancer will review it against the confirmed plan
          {submittedCount > 1 ? ` (${submittedCount} sent so far)` : ""}. You can send another one
          below if needed.
        </p>
      )}
      </ClientCard>
    </ClientFrame>
  );
}
