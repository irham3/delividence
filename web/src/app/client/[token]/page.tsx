"use client";

import { use, useEffect, useState } from "react";
import { ClientCard, ClientFrame } from "@/components/delividence/client-frame";
import {
  apiFetch,
  type AcceptanceCriterion,
  type ClientView,
  type Deliverable,
} from "@/lib/api";

const NOT_SET = "NOT_SET";

export default function ClientClarificationPage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = use(params);

  const [view, setView] = useState<ClientView | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [confirmError, setConfirmError] = useState<string | null>(null);
  const [confirmed, setConfirmed] = useState<{ version: number } | null>(null);
  const [saving, setSaving] = useState(false);
  const [confirming, setConfirming] = useState(false);

  const [deliverables, setDeliverables] = useState<Deliverable[]>([]);
  const [criteria, setCriteria] = useState<AcceptanceCriterion[]>([]);
  const [inScope, setInScope] = useState<string[]>([]);
  const [outOfScope, setOutOfScope] = useState<string[]>([]);
  const [dependencies, setDependencies] = useState<string[]>([]);
  const [assumptions, setAssumptions] = useState<string[]>([]);
  const [unresolvedQuestions, setUnresolvedQuestions] = useState<string[]>([]);
  const [deadline, setDeadline] = useState("");
  const [roundsTotal, setRoundsTotal] = useState<string>("");
  const [roundsNotSet, setRoundsNotSet] = useState(false);

  async function load() {
    try {
      const v = await apiFetch<ClientView>(`/client/${token}`);
      setView(v);
      setLoadError(null);
      const l = v.ledger;
      setDeliverables(l.deliverables?.value ?? []);
      setCriteria(l.acceptance_criteria?.value ?? []);
      setInScope(l.in_scope?.value ?? []);
      setOutOfScope(l.out_of_scope?.value ?? []);
      setDependencies(l.dependencies?.value ?? []);
      setAssumptions(l.assumptions?.value ?? []);
      setUnresolvedQuestions(l.unresolved_questions?.value ?? []);
      setDeadline(l.timeline?.final_deadline?.value ?? "");
      const rt = l.revision_policy?.rounds_total?.value;
      if (rt === NOT_SET) {
        setRoundsNotSet(true);
        setRoundsTotal("");
      } else if (typeof rt === "number") {
        setRoundsNotSet(false);
        setRoundsTotal(String(rt));
      }
    } catch (e) {
      setLoadError(e instanceof Error ? e.message : "Failed to load this link.");
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function saveAnswers() {
    setSaving(true);
    setSaveError(null);
    try {
      const answers: { field: string; value: unknown }[] = [
        { field: "deliverables", value: deliverables },
        { field: "acceptance_criteria", value: criteria },
        { field: "in_scope", value: inScope },
        { field: "out_of_scope", value: outOfScope },
        { field: "dependencies", value: dependencies },
        { field: "assumptions", value: assumptions },
        { field: "unresolved_questions", value: unresolvedQuestions },
        { field: "timeline.final_deadline", value: deadline || null },
        {
          field: "revision_policy.rounds_total",
          value: roundsNotSet ? NOT_SET : roundsTotal === "" ? null : Number(roundsTotal),
        },
      ];
      await apiFetch(`/client/${token}/answers`, {
        method: "POST",
        body: JSON.stringify({ answers }),
      });
      await load();
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : "Failed to save.");
    } finally {
      setSaving(false);
    }
  }

  async function confirmPlan() {
    if (!view) return;
    setConfirming(true);
    setConfirmError(null);
    try {
      const result = await apiFetch<{ version: number }>(`/client/${token}/confirm`, {
        method: "POST",
        body: JSON.stringify({ payload_hash: view.payload_hash }),
      });
      setConfirmed(result);
    } catch (e) {
      setConfirmError(e instanceof Error ? e.message : "Failed to confirm.");
      await load();
    } finally {
      setConfirming(false);
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
      <ClientFrame title="Loading plan">
        <ClientCard>
          <p className="text-sm text-[var(--muted)]">Loading...</p>
        </ClientCard>
      </ClientFrame>
    );
  }

  if (confirmed) {
    return (
      <ClientFrame title="Project plan confirmed">
        <ClientCard>
        <p className="text-sm leading-6 text-[var(--muted)]">
          Baseline version {confirmed.version} is now active. The freelancer can start work
          against this plan.
        </p>
        </ClientCard>
      </ClientFrame>
    );
  }

  return (
    <ClientFrame
      title="Review the project plan"
      description="Resolve the few parts the record cannot assume, then confirm the version your freelancer should work from."
    >
      <ClientCard>
      <p className="whitespace-pre-wrap rounded-[6px] border border-[var(--rule)] bg-[var(--surface-strong)] p-4 text-sm leading-6 text-[var(--muted)]">
        {view.brief}
      </p>

      <ReadinessBanner ready={view.readiness.ready} blockers={view.readiness.blockers} />

      <section className="mt-8 space-y-8">
        <ListField
          label="Deliverables"
          items={deliverables}
          onChange={setDeliverables}
          empty={{ id: "", title: "" }}
          render={(item, onEdit) => (
            <>
              <input
                value={item.id}
                onChange={(e) => onEdit({ ...item, id: e.target.value })}
                placeholder="id (e.g. d1)"
                className="w-24 rounded border border-[var(--rule)] surface-o60 px-2 py-1 text-sm"
              />
              <input
                value={item.title}
                onChange={(e) => onEdit({ ...item, title: e.target.value })}
                placeholder="Title, e.g. Landing page"
                className="flex-1 rounded border border-[var(--rule)] surface-o60 px-2 py-1 text-sm"
              />
            </>
          )}
        />

        <ListField
          label="Acceptance criteria"
          items={criteria}
          onChange={setCriteria}
          empty={{ deliverable_id: deliverables[0]?.id ?? "", criterion_key: "", text: "" }}
          render={(item, onEdit) => (
            <>
              <select
                value={item.deliverable_id}
                onChange={(e) => onEdit({ ...item, deliverable_id: e.target.value })}
                className="w-32 rounded border border-[var(--rule)] surface-o60 px-2 py-1 text-sm"
              >
                <option value="">deliverable</option>
                {deliverables.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.id}
                  </option>
                ))}
              </select>
              <input
                value={item.criterion_key}
                onChange={(e) => onEdit({ ...item, criterion_key: e.target.value })}
                placeholder="key (e.g. mobile-breakpoints)"
                className="w-40 rounded border border-[var(--rule)] surface-o60 px-2 py-1 text-sm"
              />
              <input
                value={item.text}
                onChange={(e) => onEdit({ ...item, text: e.target.value })}
                placeholder="What must be true for this to be done?"
                className="flex-1 rounded border border-[var(--rule)] surface-o60 px-2 py-1 text-sm"
              />
            </>
          )}
        />

        <ListField
          label="Out of scope"
          items={outOfScope}
          onChange={setOutOfScope}
          empty=""
          render={(item, onEdit) => (
            <input
              value={item}
              onChange={(e) => onEdit(e.target.value)}
              placeholder="Something explicitly excluded"
              className="flex-1 rounded border border-[var(--rule)] surface-o60 px-2 py-1 text-sm"
            />
          )}
        />

        <div>
          <label className="text-sm font-medium">Final deadline</label>
          <input
            type="date"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            className="focus-ring mt-1 block rounded-[6px] border border-[var(--rule)] bg-[var(--surface-strong)] px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="text-sm font-medium">Revision rounds included</label>
          <div className="mt-1 flex items-center gap-3">
            <input
              type="number"
              min={0}
              value={roundsTotal}
              disabled={roundsNotSet}
              onChange={(e) => setRoundsTotal(e.target.value)}
              className="focus-ring w-24 rounded-[6px] border border-[var(--rule)] bg-[var(--surface-strong)] px-3 py-2 text-sm disabled:opacity-40"
            />
            <label className="flex items-center gap-1 text-xs text-[var(--muted)]">
              <input
                type="checkbox"
                checked={roundsNotSet}
                onChange={(e) => setRoundsNotSet(e.target.checked)}
              />
              No limit set (explicitly)
            </label>
          </div>
        </div>

        <div className="border-t border-[var(--rule)] pt-6">
          <p className="text-sm font-medium">Additional context</p>
          <p className="mt-1 text-xs text-[var(--muted)]">
            Not required to confirm the plan, but helps avoid surprises later.
          </p>
          <div className="mt-4 space-y-6">
            <ListField
              label="In scope"
              items={inScope}
              onChange={setInScope}
              empty=""
              render={(item, onEdit) => (
                <input
                  value={item}
                  onChange={(e) => onEdit(e.target.value)}
                  placeholder="Something explicitly included"
                  className="flex-1 rounded border border-[var(--rule)] surface-o60 px-2 py-1 text-sm"
                />
              )}
            />
            <ListField
              label="Dependencies / client responsibilities"
              items={dependencies}
              onChange={setDependencies}
              empty=""
              render={(item, onEdit) => (
                <input
                  value={item}
                  onChange={(e) => onEdit(e.target.value)}
                  placeholder="Something the client needs to provide"
                  className="flex-1 rounded border border-[var(--rule)] surface-o60 px-2 py-1 text-sm"
                />
              )}
            />
            <ListField
              label="Assumptions"
              items={assumptions}
              onChange={setAssumptions}
              empty=""
              render={(item, onEdit) => (
                <input
                  value={item}
                  onChange={(e) => onEdit(e.target.value)}
                  placeholder="Something being assumed true"
                  className="flex-1 rounded border border-[var(--rule)] surface-o60 px-2 py-1 text-sm"
                />
              )}
            />
            <ListField
              label="Unresolved questions"
              items={unresolvedQuestions}
              onChange={setUnresolvedQuestions}
              empty=""
              render={(item, onEdit) => (
                <input
                  value={item}
                  onChange={(e) => onEdit(e.target.value)}
                  placeholder="Something still unclear"
                  className="flex-1 rounded border border-[var(--rule)] surface-o60 px-2 py-1 text-sm"
                />
              )}
            />
          </div>
        </div>
      </section>

      {saveError && <p className="mt-4 text-sm text-[var(--danger)]">{saveError}</p>}

      <div className="mt-8 flex items-center gap-3 border-t border-[var(--rule)] pt-6">
        <button
          onClick={saveAnswers}
          disabled={saving}
          className="tap focus-ring rounded-[6px] border border-[var(--rule)] surface-o55 px-4 py-2 text-sm disabled:opacity-40"
        >
          {saving ? "Saving..." : "Save changes"}
        </button>
        <button
          onClick={confirmPlan}
          disabled={!view.readiness.ready || confirming || saving}
          title={
            !view.readiness.ready
              ? "Resolve all blockers first"
              : saving
                ? "Wait for your saved changes before confirming"
                : undefined
          }
          className="tap focus-ring rounded-[6px] bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
        >
          {confirming ? "Confirming..." : "Confirm project plan"}
        </button>
      </div>
      {confirmError && <p className="mt-3 text-sm text-[var(--danger)]">{confirmError}</p>}
      </ClientCard>
    </ClientFrame>
  );
}

function ReadinessBanner({
  ready,
  blockers,
}: {
  ready: boolean;
  blockers: { field: string; reason: string }[];
}) {
  if (ready) {
    return (
      <p className="mt-6 rounded-md status-ok p-3 text-sm">
        Everything critical is filled in. You can confirm the project plan.
      </p>
    );
  }
  return (
    <div className="mt-6 rounded-md status-warn p-3 text-sm">
      <p className="font-medium">A few things still need your input:</p>
      <ul className="mt-2 list-disc space-y-1 pl-5">
        {blockers.map((b, i) => (
          <li key={i}>
        <span className="font-mono text-xs">{b.field}</span> - {b.reason}
          </li>
        ))}
      </ul>
    </div>
  );
}

function ListField<T>({
  label,
  items,
  onChange,
  empty,
  render,
}: {
  label: string;
  items: T[];
  onChange: (items: T[]) => void;
  empty: T;
  render: (item: T, onEdit: (next: T) => void) => React.ReactNode;
}) {
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <label className="text-sm font-medium">{label}</label>
        <button
          type="button"
          onClick={() => onChange([...items, empty])}
          className="text-xs text-[var(--muted)] underline"
        >
          + add
        </button>
      </div>
      <div className="mt-2 space-y-2">
        {items.map((item, i) => (
          <div key={i} className="flex items-center gap-2">
            {render(item, (next) => onChange(items.map((it, j) => (j === i ? next : it))))}
            <button
              type="button"
              onClick={() => onChange(items.filter((_, j) => j !== i))}
              className="shrink-0 text-xs text-[var(--faint)] hover:text-[var(--danger)]"
            >
              remove
            </button>
          </div>
        ))}
        {items.length === 0 && (
          <p className="text-xs text-[var(--faint)]">Nothing yet - add one above.</p>
        )}
      </div>
    </div>
  );
}
