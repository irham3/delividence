"use client";

import { use, useEffect, useState } from "react";
import { ClientCard, ClientFrame } from "@/components/delividence/client-frame";
import { apiFetch, type ReviewCriterion, type ReviewView } from "@/lib/api";

type Decision = "ACCEPTED" | "CHANGES_REQUESTED";

export default function DeliveryReviewPage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = use(params);

  const [view, setView] = useState<ReviewView | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [decisions, setDecisions] = useState<Record<string, Decision>>({});
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  async function load() {
    try {
      const v = await apiFetch<ReviewView>(`/client/${token}/review`);
      setView(v);
      setLoadError(null);
    } catch (e) {
      setLoadError(e instanceof Error ? e.message : "Failed to load this review.");
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function submit() {
    const items = Object.entries(decisions)
      .filter(([, decision]) => decision)
      .map(([criterion_key, decision]) => ({
        criterion_key,
        decision,
        reason: reasons[criterion_key],
      }));
    if (items.length === 0) return;

    setSubmitting(true);
    setSubmitError(null);
    try {
      await apiFetch(`/client/${token}/review`, {
        method: "POST",
        body: JSON.stringify({ decisions: items }),
      });
      setSubmitted(true);
      setDecisions({});
      setReasons({});
      await load();
    } catch (e) {
      setSubmitError(e instanceof Error ? e.message : "Failed to submit review.");
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
      <ClientFrame title="Loading review">
        <ClientCard>
          <p className="text-sm text-[var(--muted)]">Loading...</p>
        </ClientCard>
      </ClientFrame>
    );
  }

  const pending = view.criteria.filter((c) => c.status !== "ACCEPTED");

  return (
    <ClientFrame
      title="Delivery review"
      description="Review the evidence for each agreed criterion. Acceptance stays with the client."
    >
      <ClientCard>
      <p className="text-sm text-[var(--muted)]">
        Baseline version {view.baseline_version}. Review the evidence for each criterion and
        accept it or request changes.
      </p>

      {submitted && (
        <p className="mt-4 rounded-md status-ok p-3 text-sm">
          Your review was submitted.
        </p>
      )}

      <div className="mt-8 space-y-6">
        {view.criteria.map((c) => (
          <CriterionCard
            key={c.criterion_key}
            criterion={c}
            decision={decisions[c.criterion_key]}
            reason={reasons[c.criterion_key] ?? ""}
            onDecision={(d) => setDecisions((s) => ({ ...s, [c.criterion_key]: d }))}
            onReason={(r) => setReasons((s) => ({ ...s, [c.criterion_key]: r }))}
          />
        ))}
      </div>

      {submitError && <p className="mt-4 text-sm text-[var(--danger)]">{submitError}</p>}

      <div className="mt-8 border-t border-[var(--rule)] pt-6">
        <button
          onClick={submit}
          disabled={submitting || Object.keys(decisions).length === 0}
            className="tap focus-ring rounded-[6px] bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
        >
          {submitting ? "Submitting..." : "Submit review"}
        </button>
        {pending.length === 0 && (
          <p className="mt-2 text-xs text-[var(--muted)]">
            All criteria are already accepted.
          </p>
        )}
      </div>
      </ClientCard>
    </ClientFrame>
  );
}

function CriterionCard({
  criterion,
  decision,
  reason,
  onDecision,
  onReason,
}: {
  criterion: ReviewCriterion;
  decision: Decision | undefined;
  reason: string;
  onDecision: (d: Decision) => void;
  onReason: (r: string) => void;
}) {
  const locked = criterion.status === "ACCEPTED";
  return (
    <div className="rounded-[8px] border border-[var(--rule)] surface-o45 p-4">
      <div className="flex items-baseline justify-between gap-4">
        <span className="font-mono text-xs text-[var(--muted)]">{criterion.criterion_key}</span>
        <span
          className={`shrink-0 rounded px-2 py-0.5 text-xs font-medium ${
            criterion.status === "ACCEPTED"
              ? "status-ok"
              : criterion.status === "CHANGES_REQUESTED"
              ? "status-warn"
              : "status-neutral"
          }`}
        >
          {criterion.status}
        </span>
      </div>
      <p className="mt-2 text-sm">{criterion.text}</p>

      {criterion.evidence.length > 0 && (
        <ul className="mt-3 space-y-1">
          {criterion.evidence.map((e) => (
            <li key={e.evidence_id} className="text-xs text-[var(--muted)]">
              [{e.type}]{" "}
              {e.type === "url" ? (
                <a href={e.uri} target="_blank" rel="noreferrer" className="underline">
                  {e.uri}
                </a>
              ) : (
                e.uri
              )}
              {e.caption ? ` - ${e.caption}` : ""}
            </li>
          ))}
        </ul>
      )}
      {criterion.evidence.length === 0 && (
        <p className="mt-3 text-xs text-[var(--faint)]">No evidence attached yet.</p>
      )}

      {locked ? (
        <p className="mt-3 text-xs text-[var(--faint)]">
          Already accepted. Further changes go through a new request instead.
        </p>
      ) : (
        <div className="mt-3 flex items-center gap-2">
          <button
            onClick={() => onDecision("ACCEPTED")}
            className={`tap focus-ring rounded-[6px] border px-3 py-1 text-xs ${
              decision === "ACCEPTED"
                ? "status-ok-border status-ok"
                : "border-[var(--rule)]"
            }`}
          >
            Accept
          </button>
          <button
            onClick={() => onDecision("CHANGES_REQUESTED")}
            className={`tap focus-ring rounded-[6px] border px-3 py-1 text-xs ${
              decision === "CHANGES_REQUESTED"
                ? "status-warn-border status-warn"
                : "border-[var(--rule)]"
            }`}
          >
            Request changes
          </button>
          {decision === "CHANGES_REQUESTED" && (
            <input
              value={reason}
              onChange={(e) => onReason(e.target.value)}
              placeholder="Why? (required)"
              className="flex-1 rounded border border-[var(--rule)] surface-o60 px-2 py-1 text-xs"
            />
          )}
        </div>
      )}
    </div>
  );
}
