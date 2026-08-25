"use client";

import { use, useEffect, useState } from "react";
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
  const [outOfScope, setOutOfScope] = useState<string[]>([]);
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
      setOutOfScope(l.out_of_scope?.value ?? []);
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
        { field: "out_of_scope", value: outOfScope },
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

  if (confirmed) {
    return (
      <main className="mx-auto max-w-2xl px-6 py-16">
        <h1 className="text-2xl font-semibold">Project plan confirmed</h1>
        <p className="mt-2 text-sm text-neutral-600">
          Baseline version {confirmed.version} is now active. The freelancer can start work
          against this plan.
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <h1 className="text-2xl font-semibold tracking-tight">Review the project plan</h1>
      <p className="mt-2 whitespace-pre-wrap rounded-md bg-neutral-50 p-3 text-sm text-neutral-700 dark:bg-neutral-900 dark:text-neutral-300">
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
                className="w-24 rounded border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              />
              <input
                value={item.title}
                onChange={(e) => onEdit({ ...item, title: e.target.value })}
                placeholder="Title, e.g. Landing page"
                className="flex-1 rounded border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-900"
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
                className="w-32 rounded border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-900"
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
                className="w-40 rounded border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              />
              <input
                value={item.text}
                onChange={(e) => onEdit({ ...item, text: e.target.value })}
                placeholder="What must be true for this to be done?"
                className="flex-1 rounded border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-900"
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
              className="flex-1 rounded border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          )}
        />

        <div>
          <label className="text-sm font-medium">Final deadline</label>
          <input
            type="date"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            className="mt-1 block rounded border border-neutral-300 px-2 py-1 text-sm dark:border-neutral-700 dark:bg-neutral-900"
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
              className="w-24 rounded border border-neutral-300 px-2 py-1 text-sm disabled:opacity-40 dark:border-neutral-700 dark:bg-neutral-900"
            />
            <label className="flex items-center gap-1 text-xs text-neutral-500">
              <input
                type="checkbox"
                checked={roundsNotSet}
                onChange={(e) => setRoundsNotSet(e.target.checked)}
              />
              No limit set (explicitly)
            </label>
          </div>
        </div>
      </section>

      {saveError && <p className="mt-4 text-sm text-red-700">{saveError}</p>}

      <div className="mt-8 flex items-center gap-3 border-t border-neutral-200 pt-6 dark:border-neutral-800">
        <button
          onClick={saveAnswers}
          disabled={saving}
          className="rounded-md border border-neutral-300 px-4 py-2 text-sm disabled:opacity-40 dark:border-neutral-700"
        >
          {saving ? "Saving…" : "Save changes"}
        </button>
        <button
          onClick={confirmPlan}
          disabled={!view.readiness.ready || confirming}
          title={!view.readiness.ready ? "Resolve all blockers first" : undefined}
          className="rounded-md bg-neutral-900 px-4 py-2 text-sm text-white disabled:opacity-40 dark:bg-white dark:text-neutral-900"
        >
          {confirming ? "Confirming…" : "Confirm project plan"}
        </button>
      </div>
      {confirmError && <p className="mt-3 text-sm text-red-700">{confirmError}</p>}
    </main>
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
      <p className="mt-6 rounded-md bg-green-50 p-3 text-sm text-green-800">
        Everything critical is filled in. You can confirm the project plan.
      </p>
    );
  }
  return (
    <div className="mt-6 rounded-md bg-amber-50 p-3 text-sm text-amber-900">
      <p className="font-medium">A few things still need your input:</p>
      <ul className="mt-2 list-disc space-y-1 pl-5">
        {blockers.map((b, i) => (
          <li key={i}>
            <span className="font-mono text-xs">{b.field}</span> — {b.reason}
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
          className="text-xs text-neutral-500 underline"
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
              className="shrink-0 text-xs text-neutral-400 hover:text-red-600"
            >
              remove
            </button>
          </div>
        ))}
        {items.length === 0 && (
          <p className="text-xs text-neutral-400">Nothing yet — add one above.</p>
        )}
      </div>
    </div>
  );
}
