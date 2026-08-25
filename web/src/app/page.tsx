"use client";

import { useEffect, useState } from "react";
import type { User } from "firebase/auth";
import { onAuthStateChanged } from "firebase/auth";
import {
  apiFetch,
  openAuthedInNewTab,
  setAuthTokenProvider,
  type Citation,
  type ProofManifest,
  type ScopeRequest,
} from "@/lib/api";
import { auth, signInWithGoogle, signOutOwner } from "@/lib/firebase";

setAuthTokenProvider(() => (auth.currentUser ? auth.currentUser.getIdToken() : Promise.resolve(null)));

type AuditStep = { at: string; step: string; detail: string };

type Run = {
  run_id: string;
  status: string;
  output_language: string;
  brief: string;
  round: number;
  audit_trail: AuditStep[];
  active_baseline_version?: number;
};

const RUN_ID_STORAGE_KEY = "delividence_run_id";

export default function Home() {
  const [brief, setBrief] = useState("");
  const [language, setLanguage] = useState("en");
  // Persisted so refreshing the page (or coming back later) doesn't lose the
  // freelancer's in-progress run -- the actions panel below is otherwise
  // unreachable again without it.
  const [runId, setRunId] = useState<string | null>(() =>
    typeof window !== "undefined" ? localStorage.getItem(RUN_ID_STORAGE_KEY) : null
  );
  const [run, setRun] = useState<Run | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [user, setUser] = useState<User | null>(null);
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => onAuthStateChanged(auth, (u) => {
    setUser(u);
    setAuthReady(true);
  }), []);

  useEffect(() => {
    try {
      if (runId) localStorage.setItem(RUN_ID_STORAGE_KEY, runId);
      else localStorage.removeItem(RUN_ID_STORAGE_KEY);
    } catch {
      // Private browsing / storage disabled -- runId just won't survive a reload.
    }
  }, [runId]);

  // The run is processed outside the request, so the page polls until the
  // worker reports a terminal state. Fetches immediately on mount/runId
  // change (not just after the first interval tick) so a restored runId
  // shows its state right away instead of a blank "queued" flash.
  useEffect(() => {
    if (!user || !runId) return;
    if (run && (run.status === "done" || run.status === "failed")) return;

    let cancelled = false;
    async function poll() {
      try {
        const data = await apiFetch<Run>(`/runs/${runId}`);
        if (!cancelled) setRun(data);
      } catch {
        // Transient; the next tick retries.
      }
    }
    poll();
    const timer = setInterval(poll, 1000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [user, runId, run]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setRun(null);
    setSubmitting(true);
    try {
      const { run_id } = await apiFetch<{ run_id: string }>("/runs", {
        method: "POST",
        body: JSON.stringify({ brief, output_language: language }),
      });
      setRunId(run_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setSubmitting(false);
    }
  }

  if (!authReady) {
    return (
      <main className="mx-auto max-w-2xl px-6 py-16">
        <p className="text-sm text-neutral-500">Loading…</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="mx-auto max-w-2xl px-6 py-16">
        <h1 className="text-3xl font-semibold tracking-tight">Delividence</h1>
        <p className="mt-2 text-sm text-neutral-500">
          Sign in to create and manage your deals.
        </p>
        <button
          onClick={() => signInWithGoogle().catch((e) => setError(e instanceof Error ? e.message : "Sign-in failed"))}
          className="mt-6 rounded-md bg-neutral-900 px-4 py-2 text-sm text-white dark:bg-white dark:text-neutral-900"
        >
          Sign in with Google
        </button>
        {error && (
          <p className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p>
        )}
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <div className="flex items-baseline justify-between gap-4">
        <h1 className="text-3xl font-semibold tracking-tight">Delividence</h1>
        <div className="flex items-center gap-2 text-xs text-neutral-500">
          <span>{user.email}</span>
          <button onClick={() => signOutOwner()} className="underline">
            Sign out
          </button>
        </div>
      </div>
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
          <div className="flex items-baseline justify-between gap-4">
            <h2 className="text-sm font-medium">Run</h2>
            <div className="flex items-center gap-3">
              <code className="text-xs text-neutral-500">{runId}</code>
              <button
                onClick={() => {
                  setRunId(null);
                  setRun(null);
                  setBrief("");
                }}
                className="text-xs text-neutral-500 underline"
              >
                Start a new run
              </button>
            </div>
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

      {runId && <FreelancerActions runId={runId} run={run} />}
    </main>
  );
}

function FreelancerActions({ runId, run }: { runId: string; run: Run | null }) {
  const [clarificationLink, setClarificationLink] = useState<string | null>(null);
  const [reviewLink, setReviewLink] = useState<string | null>(null);
  const [linkError, setLinkError] = useState<string | null>(null);

  const [criterionKey, setCriterionKey] = useState("");
  const [evidenceType, setEvidenceType] = useState<"url" | "text">("url");
  const [evidenceUri, setEvidenceUri] = useState("");
  const [evidenceCaption, setEvidenceCaption] = useState("");
  const [evidenceMessage, setEvidenceMessage] = useState<string | null>(null);
  const [evidenceSaving, setEvidenceSaving] = useState(false);

  const origin = typeof window !== "undefined" ? window.location.origin : "";

  async function createLink(purpose: "CLARIFICATION" | "DELIVERY_REVIEW") {
    setLinkError(null);
    try {
      const { token } = await apiFetch<{ token: string }>(`/runs/${runId}/client-links`, {
        method: "POST",
        body: JSON.stringify({ purpose }),
      });
      const url =
        purpose === "CLARIFICATION"
          ? `${origin}/client/${token}`
          : `${origin}/client/${token}/review`;
      if (purpose === "CLARIFICATION") setClarificationLink(url);
      else setReviewLink(url);
    } catch (e) {
      setLinkError(e instanceof Error ? e.message : "Failed to create link.");
    }
  }

  async function addEvidence(event: React.FormEvent) {
    event.preventDefault();
    setEvidenceSaving(true);
    setEvidenceMessage(null);
    try {
      await apiFetch(`/runs/${runId}/evidence`, {
        method: "POST",
        body: JSON.stringify({
          criterion_key: criterionKey,
          type: evidenceType,
          uri: evidenceUri,
          caption: evidenceCaption || null,
        }),
      });
      setEvidenceMessage("Evidence attached.");
      setCriterionKey("");
      setEvidenceUri("");
      setEvidenceCaption("");
    } catch (e) {
      setEvidenceMessage(e instanceof Error ? e.message : "Failed to attach evidence.");
    } finally {
      setEvidenceSaving(false);
    }
  }

  const hasBaseline = !!run?.active_baseline_version;

  return (
    <section className="mt-10 space-y-8 border-t border-neutral-200 pt-6 dark:border-neutral-800">
      <h2 className="text-sm font-medium">Freelancer actions</h2>

      <div>
        <p className="text-sm text-neutral-600 dark:text-neutral-400">
          Send this link to the client so they can review and confirm the plan.
        </p>
        <div className="mt-2 flex items-center gap-3">
          <button
            onClick={() => createLink("CLARIFICATION")}
            className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm dark:border-neutral-700"
          >
            Create clarification link
          </button>
          {clarificationLink && (
            <code className="truncate text-xs text-neutral-500">{clarificationLink}</code>
          )}
        </div>
      </div>

      <div>
        <p className="text-sm text-neutral-600 dark:text-neutral-400">
          {hasBaseline
            ? "Once the plan is confirmed, send this link for delivery review."
            : "Available once the client confirms the project plan."}
        </p>
        <div className="mt-2 flex items-center gap-3">
          <button
            onClick={() => createLink("DELIVERY_REVIEW")}
            disabled={!hasBaseline}
            className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm disabled:opacity-40 dark:border-neutral-700"
          >
            Create delivery review link
          </button>
          {reviewLink && <code className="truncate text-xs text-neutral-500">{reviewLink}</code>}
        </div>
      </div>
      {linkError && <p className="text-sm text-red-700">{linkError}</p>}

      <div>
        <p className="text-sm text-neutral-600 dark:text-neutral-400">
          Attach evidence to an acceptance criterion (needs a confirmed plan).
        </p>
        <form onSubmit={addEvidence} className="mt-2 flex flex-wrap items-center gap-2">
          <input
            value={criterionKey}
            onChange={(e) => setCriterionKey(e.target.value)}
            required
            disabled={!hasBaseline}
            placeholder="criterion key"
            className="w-40 rounded border border-neutral-300 px-2 py-1 text-sm disabled:opacity-40 dark:border-neutral-700 dark:bg-neutral-900"
          />
          <select
            value={evidenceType}
            onChange={(e) => setEvidenceType(e.target.value as "url" | "text")}
            disabled={!hasBaseline}
            className="rounded border border-neutral-300 px-2 py-1 text-sm disabled:opacity-40 dark:border-neutral-700 dark:bg-neutral-900"
          >
            <option value="url">url</option>
            <option value="text">text</option>
          </select>
          <input
            value={evidenceUri}
            onChange={(e) => setEvidenceUri(e.target.value)}
            required
            disabled={!hasBaseline}
            placeholder={evidenceType === "url" ? "https://…" : "Test result text"}
            className="min-w-48 flex-1 rounded border border-neutral-300 px-2 py-1 text-sm disabled:opacity-40 dark:border-neutral-700 dark:bg-neutral-900"
          />
          <input
            value={evidenceCaption}
            onChange={(e) => setEvidenceCaption(e.target.value)}
            disabled={!hasBaseline}
            placeholder="caption (optional)"
            className="w-40 rounded border border-neutral-300 px-2 py-1 text-sm disabled:opacity-40 dark:border-neutral-700 dark:bg-neutral-900"
          />
          <button
            type="submit"
            disabled={!hasBaseline || evidenceSaving}
            className="rounded-md bg-neutral-900 px-3 py-1.5 text-sm text-white disabled:opacity-40 dark:bg-white dark:text-neutral-900"
          >
            {evidenceSaving ? "Saving…" : "Attach"}
          </button>
        </form>
        {evidenceMessage && (
          <p className="mt-2 text-xs text-neutral-500">{evidenceMessage}</p>
        )}
      </div>

      <div>
        <p className="text-sm text-neutral-600 dark:text-neutral-400">
          {hasBaseline
            ? "Acceptance Record, exportable as JSON or Markdown."
            : "Proof export is available once a baseline is confirmed."}
        </p>
        <div className="mt-2 flex items-center gap-3 text-sm">
          <button
            onClick={() => openAuthedInNewTab(`/runs/${runId}/proof?format=json`)}
            disabled={!hasBaseline}
            className="underline disabled:pointer-events-none disabled:opacity-40"
          >
            View JSON
          </button>
          <button
            onClick={() => openAuthedInNewTab(`/runs/${runId}/proof?format=md`)}
            disabled={!hasBaseline}
            className="underline disabled:pointer-events-none disabled:opacity-40"
          >
            View Markdown
          </button>
        </div>
      </div>

      {hasBaseline && <GuardrailPanel runId={runId} />}
    </section>
  );
}

const CLASSIFICATIONS = ["IN_SCOPE", "AMBIGUOUS", "CHANGE_REQUEST"] as const;
type Classification = (typeof CLASSIFICATIONS)[number];

function GuardrailPanel({ runId }: { runId: string }) {
  const [requests, setRequests] = useState<ScopeRequest[]>([]);
  const [citableRefs, setCitableRefs] = useState<{ ref: string; text: string }[]>([]);
  const [rawText, setRawText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      const [reqs, proof] = await Promise.all([
        apiFetch<ScopeRequest[]>(`/runs/${runId}/requests`),
        apiFetch<ProofManifest>(`/runs/${runId}/proof?format=json`),
      ]);
      setRequests(reqs);
      setCitableRefs(proof.criteria.map((c) => ({ ref: c.criterion_key, text: c.text })));
    } catch {
      // Best-effort -- panel just stays empty/stale until the next load().
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId]);

  async function submitRequest(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await apiFetch(`/runs/${runId}/requests`, {
        method: "POST",
        body: JSON.stringify({ raw_text: rawText, submitted_by: "freelancer" }),
      });
      setRawText("");
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to log request.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="border-t border-neutral-200 pt-8 dark:border-neutral-800">
      <h2 className="text-sm font-medium">New requests (Guardrail)</h2>
      <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
        Log something the client asked for after the plan was confirmed. Classify it against
        the baseline with a verbatim citation -- without one it&apos;s automatically downgraded
        to AMBIGUOUS, never assumed in scope.
      </p>

      <form onSubmit={submitRequest} className="mt-3 flex items-center gap-2">
        <input
          value={rawText}
          onChange={(e) => setRawText(e.target.value)}
          required
          placeholder="What did the client ask for?"
          className="min-w-48 flex-1 rounded border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-900"
        />
        <button
          type="submit"
          disabled={submitting}
          className="rounded-md bg-neutral-900 px-3 py-1.5 text-sm text-white disabled:opacity-40 dark:bg-white dark:text-neutral-900"
        >
          {submitting ? "Logging…" : "Log request"}
        </button>
      </form>
      {error && <p className="mt-2 text-xs text-red-700">{error}</p>}

      <div className="mt-4 space-y-3">
        {requests.map((r) => (
          <RequestCard
            key={r.request_id}
            runId={runId}
            request={r}
            citableRefs={citableRefs}
            onClassified={load}
          />
        ))}
        {requests.length === 0 && (
          <p className="text-xs text-neutral-400">No requests logged yet.</p>
        )}
      </div>
    </div>
  );
}

function RequestCard({
  runId,
  request,
  citableRefs,
  onClassified,
}: {
  runId: string;
  request: ScopeRequest;
  citableRefs: { ref: string; text: string }[];
  onClassified: () => void;
}) {
  const [classification, setClassification] = useState<Classification>("AMBIGUOUS");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function classify() {
    setSubmitting(true);
    setError(null);
    try {
      await apiFetch(`/runs/${runId}/requests/${request.request_id}/classify`, {
        method: "POST",
        body: JSON.stringify({ classification, citations }),
      });
      onClassified();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to classify.");
    } finally {
      setSubmitting(false);
    }
  }

  if (request.confirmed_classification) {
    return (
      <div className="rounded-md border border-neutral-200 p-3 text-sm dark:border-neutral-800">
        <p>{request.raw_text}</p>
        <p className="mt-1 text-xs">
          Classification: <strong>{request.confirmed_classification}</strong>
        </p>
        {request.citations.length > 0 && (
          <ul className="mt-1 space-y-0.5 text-xs text-neutral-500">
            {request.citations.map((c, i) => (
              <li key={i}>
                <code>{c.ref}</code> — &quot;{c.quote}&quot;
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  return (
    <div className="rounded-md border border-neutral-200 p-3 text-sm dark:border-neutral-800">
      <p>{request.raw_text}</p>
      <div className="mt-2 flex items-center gap-2">
        <select
          value={classification}
          onChange={(e) => setClassification(e.target.value as Classification)}
          className="rounded border border-neutral-300 px-2 py-1 text-xs dark:border-neutral-700 dark:bg-neutral-900"
        >
          {CLASSIFICATIONS.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <button
          onClick={classify}
          disabled={submitting}
          className="rounded-md border border-neutral-300 px-3 py-1 text-xs disabled:opacity-40 dark:border-neutral-700"
        >
          {submitting ? "Saving…" : "Confirm classification"}
        </button>
      </div>

      {classification !== "AMBIGUOUS" && (
        <div className="mt-2">
          {citableRefs.length > 0 && (
            <ul className="space-y-0.5 text-xs text-neutral-400">
              {citableRefs.map((c) => (
                <li key={c.ref}>
                  <code>{c.ref}</code>: {c.text}
                </li>
              ))}
            </ul>
          )}
          <CitationList citations={citations} onChange={setCitations} />
        </div>
      )}
      {error && <p className="mt-2 text-xs text-red-700">{error}</p>}
    </div>
  );
}

function CitationList({
  citations,
  onChange,
}: {
  citations: Citation[];
  onChange: (c: Citation[]) => void;
}) {
  return (
    <div className="mt-1 space-y-1">
      {citations.map((c, i) => (
        <div key={i} className="flex items-center gap-1">
          <input
            value={c.ref}
            onChange={(e) =>
              onChange(citations.map((it, j) => (j === i ? { ...it, ref: e.target.value } : it)))
            }
            placeholder="ref"
            className="w-32 rounded border border-neutral-300 px-1 py-0.5 text-xs dark:border-neutral-700 dark:bg-neutral-900"
          />
          <input
            value={c.quote}
            onChange={(e) =>
              onChange(citations.map((it, j) => (j === i ? { ...it, quote: e.target.value } : it)))
            }
            placeholder="verbatim quote"
            className="flex-1 rounded border border-neutral-300 px-1 py-0.5 text-xs dark:border-neutral-700 dark:bg-neutral-900"
          />
          <button
            type="button"
            onClick={() => onChange(citations.filter((_, j) => j !== i))}
            className="text-xs text-neutral-400"
          >
            remove
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={() => onChange([...citations, { ref: "", quote: "" }])}
        className="text-xs text-neutral-500 underline"
      >
        + add citation
      </button>
    </div>
  );
}
