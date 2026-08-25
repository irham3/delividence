"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8080";

type AuditStep = { at: string; step: string; detail: string };

type Run = {
  run_id: string;
  status: string;
  output_language: string;
  brief: string;
  round: number;
  audit_trail: AuditStep[];
};

export default function Home() {
  const [brief, setBrief] = useState("");
  const [language, setLanguage] = useState("en");
  const [runId, setRunId] = useState<string | null>(null);
  const [run, setRun] = useState<Run | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // The run is processed outside the request, so the page polls until the
  // worker reports a terminal state.
  useEffect(() => {
    if (!runId) return;
    if (run && (run.status === "done" || run.status === "failed")) return;

    const timer = setInterval(async () => {
      try {
        const res = await fetch(`${API}/runs/${runId}`);
        if (res.ok) setRun(await res.json());
      } catch {
        // Transient; the next tick retries.
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [runId, run]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setRun(null);
    setSubmitting(true);
    try {
      const res = await fetch(`${API}/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brief, output_language: language }),
      });
      if (!res.ok) throw new Error(`API returned ${res.status}`);
      setRunId((await res.json()).run_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <h1 className="text-3xl font-semibold tracking-tight">Delividence</h1>
      <p className="mt-2 text-sm text-neutral-500">
        Paste a client brief. The agent works on it in the background and records
        every step it takes.
      </p>

      <form onSubmit={submit} className="mt-8 space-y-4">
        <textarea
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          required
          rows={7}
          placeholder="Can you edit some videos for our IG? A few clips, deadline next week, budget 2 million."
          className="w-full rounded-md border border-neutral-300 p-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
        />

        <div className="flex items-center gap-3">
          <label htmlFor="lang" className="text-sm text-neutral-500">
            Output language
          </label>
          <select
            id="lang"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="rounded-md border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          >
            <option value="en">English</option>
            <option value="id">Bahasa Indonesia</option>
          </select>

          <button
            type="submit"
            disabled={submitting || brief.trim().length === 0}
            className="ml-auto rounded-md bg-neutral-900 px-4 py-2 text-sm text-white disabled:opacity-40 dark:bg-white dark:text-neutral-900"
          >
            {submitting ? "Sending…" : "Analyse brief"}
          </button>
        </div>
      </form>

      {error && (
        <p className="mt-6 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p>
      )}

      {runId && (
        <section className="mt-10 border-t border-neutral-200 pt-6 dark:border-neutral-800">
          <div className="flex items-baseline justify-between">
            <h2 className="text-sm font-medium">Run</h2>
            <code className="text-xs text-neutral-500">{runId}</code>
          </div>

          <p className="mt-2 text-sm">
            Status: <strong>{run?.status ?? "queued"}</strong>
          </p>

          <ol className="mt-4 space-y-3">
            {(run?.audit_trail ?? []).map((step, i) => (
              <li
                key={i}
                className="rounded-md border border-neutral-200 p-3 text-sm dark:border-neutral-800"
              >
                <div className="flex justify-between gap-4">
                  <span className="font-medium">{step.step}</span>
                  <time className="shrink-0 text-xs text-neutral-500">
                    {new Date(step.at).toLocaleTimeString()}
                  </time>
                </div>
                <p className="mt-1 text-neutral-600 dark:text-neutral-400">
                  {step.detail}
                </p>
              </li>
            ))}
          </ol>

          {run && run.audit_trail.length === 0 && (
            <p className="mt-4 text-sm text-neutral-500">
              Waiting for the worker to pick this up…
            </p>
          )}
        </section>
      )}
    </main>
  );
}
