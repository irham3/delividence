"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  FileText,
  FolderOpen,
  ListChecks,
  Plus,
  RefreshCw,
  Upload,
} from "lucide-react";
import { OwnerGate } from "@/components/delividence/owner-gate";
import { fieldSummary } from "@/lib/ledger-summary";
import {
  apiFetch,
  type ActiveBaseline,
  type AuditEvent,
  type OwnerPreference,
  type OwnerRun,
  type ScopeRequest,
} from "@/lib/api";

type IndexMode = "records" | "sources" | "review" | "activity" | "policies";
type DetailMode = "sources" | "questions" | "baseline" | "evidence" | "activity" | "requests";

const pageMeta: Record<IndexMode, { title: string; description: string }> = {
  records: { title: "Records", description: "Find a deal and see the decision it needs next." },
  sources: { title: "Sources", description: "Inspect what was said before relying on the record." },
  review: { title: "Review", description: "Keep agreement, evidence, and client decisions in view." },
  activity: { title: "Activity", description: "Chronological facts only. Nothing is silently replaced." },
  policies: { title: "Working policies", description: "Policies guide drafts. They never replace a client’s words." },
};

function useRuns() {
  const [items, setItems] = useState<OwnerRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  async function refresh() {
    setLoading(true);
    try {
      const result = await apiFetch<{ items: OwnerRun[] }>("/runs");
      setItems(result.items);
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not load records.");
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount
    refresh();
  }, []);
  return { items, loading, error, refresh };
}

export function OwnerIndex({ mode }: { mode: IndexMode }) {
  return <OwnerGate>{() => <OwnerIndexContent mode={mode} />}</OwnerGate>;
}

function OwnerIndexContent({ mode }: { mode: IndexMode }) {
  const { items, loading, error, refresh } = useRuns();
  const meta = pageMeta[mode];
  if (mode === "policies") return <PolicyView />;

  return (
    <section>
      <PageHeading title={meta.title} description={meta.description} action={<button onClick={refresh} className="tap focus-ring inline-flex items-center gap-2 rounded-[4px] border border-[var(--rule)] px-3 py-2 text-sm"><RefreshCw size={15} /> Refresh</button>} />
      {error && <Message tone="error">{error}</Message>}
      {loading ? <RecordSkeleton /> : items.length === 0 ? <EmptyRecords /> : <RecordIndex mode={mode} records={items} />}
    </section>
  );
}

function RecordIndex({ mode, records }: { mode: Exclude<IndexMode, "policies">; records: OwnerRun[] }) {
  const Icon = mode === "sources" ? FolderOpen : mode === "review" ? ListChecks : mode === "activity" ? Activity : FileText;
  return (
    <div className="paper-card overflow-hidden rounded-[8px]">
      <div className="hidden grid-cols-[minmax(220px,1.4fr)_150px_120px_160px] gap-5 border-b border-[var(--rule)] px-6 py-3 text-[11px] font-medium uppercase tracking-[0.1em] text-[var(--muted)] md:grid"><span>Record</span><span>Status</span><span>Baseline</span><span>Open</span></div>
      {records.map((record) => {
        const detailMode = mode === "review" ? "evidence" : mode;
        const target = `/records/${record.run_id}/${detailMode}`;
        return (
          <Link key={record.run_id} href={target} className="tap focus-ring grid gap-3 border-b border-[var(--rule)] px-5 py-5 last:border-b-0 hover:surface-o45 md:grid-cols-[minmax(220px,1.4fr)_150px_120px_160px] md:items-center md:gap-5 md:px-6">
            <div className="min-w-0"><p className="truncate font-medium">{recordTitle(record)}</p><p className="mt-1 truncate text-sm text-[var(--muted)]">{record.brief}</p></div>
            <Status value={record.status} />
            <span className="text-sm text-[var(--muted)]">{record.active_baseline_version ? `v${record.active_baseline_version}` : "Draft"}</span>
            <span className="inline-flex items-center gap-2 text-sm"><Icon size={15} className="text-[var(--accent)]" /> Open <ArrowRight size={15} className="text-[var(--accent)]" /></span>
          </Link>
        );
      })}
    </div>
  );
}

function EmptyRecords() {
  return <div className="paper-card rounded-[8px] px-6 py-16 text-center"><FolderOpen className="mx-auto text-[var(--accent)]" size={26} strokeWidth={1.5} /><h2 className="mt-5 text-xl font-semibold">No records yet.</h2><p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-[var(--muted)]">Start with the material you already have. Delividence will only ask for what the record cannot answer.</p><Link href="/records/new" className="tap focus-ring mt-7 inline-flex items-center gap-2 rounded-[4px] bg-[var(--accent)] px-4 py-3 text-sm font-medium text-white"><Plus size={16} /> Create a record</Link></div>;
}

function RecordSkeleton() {
  return <div className="paper-card space-y-4 rounded-[8px] p-6" aria-label="Loading records"><div className="h-5 w-2/5 animate-pulse bg-[var(--rule)]/60" /><div className="h-12 animate-pulse bg-[var(--rule)]/45" /><div className="h-12 animate-pulse bg-[var(--rule)]/35" /></div>;
}

export function NewRecord() {
  return <OwnerGate>{() => <NewRecordContent />}</OwnerGate>;
}

function NewRecordContent() {
  const [brief, setBrief] = useState("");
  const [language, setLanguage] = useState("en");
  const [saving, setSaving] = useState(false);
  const [result, setResult] = useState<{ run_id: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  async function create(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true); setError(null);
    try {
      const next = await apiFetch<{ run_id: string }>("/runs", { method: "POST", body: JSON.stringify({ brief, output_language: language }) });
      setResult(next);
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Could not create this record."); }
    finally { setSaving(false); }
  }
  return <section><PageHeading title="Start with the material you already have." description="Paste a brief, email export, chat note, transcript, screenshot reference, or video reference. The first build accepts text; upload adapters are prepared for the cloud handoff." />
    <form onSubmit={create} className="paper-card rounded-[8px] p-5 sm:p-7">
      <label htmlFor="brief" className="text-sm font-medium">Project material</label>
      <textarea id="brief" required value={brief} onChange={(event) => setBrief(event.target.value)} rows={12} placeholder="Paste the client material here..." className="focus-ring mt-3 w-full rounded-[4px] border border-[var(--rule)] bg-[var(--surface-strong)] p-4 text-sm leading-6 placeholder:text-[var(--faint)]" />
      <div className="mt-4 flex flex-wrap items-center justify-between gap-4"><label className="flex items-center gap-2 text-sm text-[var(--muted)]">Output language <select value={language} onChange={(event) => setLanguage(event.target.value)} className="focus-ring rounded-[4px] border border-[var(--rule)] bg-[var(--surface-strong)] px-2 py-1.5 text-[var(--ink)]"><option value="en">English</option><option value="id">Bahasa Indonesia</option></select></label><button disabled={saving || !brief.trim()} className="tap focus-ring inline-flex min-h-11 items-center gap-2 rounded-[4px] bg-[var(--accent)] px-4 text-sm font-medium text-white disabled:opacity-40"><Upload size={16} />{saving ? "Creating..." : "Read the material"}</button></div>
      {error && <Message tone="error">{error}</Message>}
      {result && <Message tone="success">Record created. <Link className="underline" href={`/records/${result.run_id}/sources`}>Open the source record.</Link></Message>}
    </form></section>;
}

export function RecordDetail({ runId, mode }: { runId: string; mode: DetailMode }) {
  return <OwnerGate>{() => <RecordDetailContent runId={runId} mode={mode} />}</OwnerGate>;
}

function RecordDetailContent({ runId, mode }: { runId: string; mode: DetailMode }) {
  const [run, setRun] = useState<OwnerRun | null>(null);
  const [activity, setActivity] = useState<AuditEvent[]>([]);
  const [baseline, setBaseline] = useState<ActiveBaseline | null>(null);
  const [requests, setRequests] = useState<ScopeRequest[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const current = await apiFetch<OwnerRun>(`/runs/${runId}`);
        if (!active) return;
        setRun(current); setError(null);
        const work: Promise<unknown>[] = [];
        if (mode === "activity") work.push(apiFetch<{ items: AuditEvent[] }>(`/runs/${runId}/activity`).then((value) => active && setActivity(value.items)));
        if (["baseline", "evidence", "requests"].includes(mode) && current.active_baseline_version) work.push(apiFetch<ActiveBaseline>(`/runs/${runId}/baseline`).then((value) => active && setBaseline(value)));
        if (mode === "requests" && current.active_baseline_version) work.push(apiFetch<ScopeRequest[]>(`/runs/${runId}/requests`).then((value) => active && setRequests(value)));
        await Promise.all(work);
      } catch (cause) { if (active) setError(cause instanceof Error ? cause.message : "Could not load this record."); }
    }
    load(); return () => { active = false; };
  }, [mode, runId]);
  const title = mode === "sources" ? "Source record" : mode === "questions" ? "Questions" : mode === "baseline" ? "Baseline" : mode === "evidence" ? "Evidence" : mode === "activity" ? "Activity" : "Change requests";
  return <section><PageHeading title={run ? `${recordTitle(run)} · ${title}` : title} description={detailDescription(mode)} action={<Link href="/records" className="focus-ring text-sm underline text-[var(--muted)]">All records</Link>} />
    {error && <Message tone="error">{error}</Message>}
    {!run ? <RecordSkeleton /> : <><RecordTabs runId={runId} active={mode} /><div className="mt-7">{mode === "sources" && <SourceDetail run={run} />}{mode === "questions" && <QuestionDetail run={run} />}{mode === "baseline" && <BaselineDetail baseline={baseline} />}{mode === "evidence" && <EvidenceDetail baseline={baseline} runId={runId} />}{mode === "activity" && <ActivityDetail items={activity} />}{mode === "requests" && <RequestsDetail items={requests} />}</div></>}
  </section>;
}

function SourceDetail({ run }: { run: OwnerRun }) {
  const ledgerEntries = Object.entries(run.ledger ?? {});
  return <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]"><article className="paper-card rounded-[8px] p-5"><p className="mono text-[11px] font-medium tracking-[0.1em] text-[var(--muted)]">SOURCE S-01</p><h2 className="mt-4 text-xl font-semibold">Client material</h2><p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-[var(--muted)]">{run.brief}</p></article><article className="paper-card rounded-[8px] p-5"><p className="mono text-[11px] font-medium tracking-[0.1em] text-[var(--muted)]">EXTRACTED LEDGER</p><div className="mt-5 grid gap-3">{ledgerEntries.length ? ledgerEntries.map(([field, value]) => <div key={field} className="border-l border-[var(--accent)] pl-4"><p className="text-sm font-medium">{field.replaceAll("_", " ")}</p><p className="mt-1 text-sm text-[var(--muted)]">{fieldSummary(value)}</p></div>) : <p className="text-sm text-[var(--muted)]">The agent is still reading this material.</p>}</div></article></div>;
}

function QuestionDetail({ run }: { run: OwnerRun }) {
  const questions = run.ledger?.unresolved_questions?.value ?? [];
  return <article className="paper-card rounded-[8px] p-5 sm:p-7"><p className="text-sm text-[var(--muted)]">Ask only what the record cannot answer. Client-facing questions are issued through a secure clarification link from the workspace.</p><div className="mt-6 space-y-3">{questions.length ? questions.map((question) => <div key={question} className="flex gap-4 border border-[var(--rule)] p-4"><span className="mono text-[var(--accent)]">?</span><p className="text-sm leading-6">{question}</p></div>) : <p className="text-sm text-[var(--muted)]">No unresolved questions are stored for this record yet.</p>}</div></article>;
}

function BaselineDetail({ baseline }: { baseline: ActiveBaseline | null }) {
  if (!baseline) return <Message tone="neutral">No active baseline yet. Send a clarification link and wait until the client confirms the project plan.</Message>;
  const payload = baseline.baseline.canonical_payload;
  return <div className="paper-card rounded-[8px] p-5 sm:p-7"><p className="mono text-[11px] tracking-[0.1em] text-[var(--muted)]">ACTIVE BASELINE v{baseline.active_version}</p><div className="mt-6 grid gap-7 lg:grid-cols-2"><DetailList title="Deliverables" values={payload.deliverables.map((deliverable) => `${deliverable.id}: ${deliverable.title}`)} /><DetailList title="Out of scope" values={payload.out_of_scope} /><DetailList title="Acceptance criteria" values={Object.entries(payload.criteria).map(([key, criterion]) => `${key}: ${criterion.text}`)} /><DetailList title="Record integrity" values={[`Hash: ${baseline.baseline.payload_hash}`, ...Object.entries(payload.timeline).map(([key, value]) => `${key}: ${String(value)}`)]} /></div></div>;
}

function EvidenceDetail({ baseline, runId }: { baseline: ActiveBaseline | null; runId: string }) {
  if (!baseline) return <Message tone="neutral">Evidence is linked after a baseline is active.</Message>;
  return <article className="paper-card rounded-[8px] p-5 sm:p-7"><p className="text-sm leading-6 text-[var(--muted)]">Attach an artifact to each criterion, then send a delivery review link. A visual check can assist, but the client records acceptance.</p><div className="mt-6 grid gap-3">{Object.entries(baseline.baseline.canonical_payload.criteria).map(([key, criterion]) => <div key={key} className="flex flex-col justify-between gap-3 border border-[var(--rule)] p-4 sm:flex-row sm:items-center"><div><p className="mono text-xs text-[var(--muted)]">{key}</p><p className="mt-1 text-sm">{criterion.text}</p></div><Link href={`/records/${runId}/evidence#${key}`} className="focus-ring text-sm text-[var(--accent)] underline">Add evidence</Link></div>)}</div></article>;
}

function ActivityDetail({ items }: { items: AuditEvent[] }) {
  return <article className="paper-card rounded-[8px] p-5 sm:p-7">{items.length ? <ol className="space-y-5">{items.map((event) => <li key={event.event_id} className="grid gap-2 border-l border-[var(--accent)] pl-4 sm:grid-cols-[150px_1fr]"><p className="mono text-xs text-[var(--muted)]">#{event.seq} · {event.actor}</p><div><p className="text-sm font-medium">{event.type.replaceAll("_", " ")}</p><p className="mt-1 text-xs text-[var(--muted)]">{new Date(event.created_at).toLocaleString()}</p></div></li>)}</ol> : <p className="text-sm text-[var(--muted)]">No audit events yet.</p>}</article>;
}

function RequestsDetail({ items }: { items: ScopeRequest[] }) {
  return <article className="paper-card rounded-[8px] p-5 sm:p-7"><p className="text-sm leading-6 text-[var(--muted)]">New work is recorded separately from the baseline. The freelancer confirms the cited classification.</p><div className="mt-6 space-y-4">{items.length ? items.map((request) => <div key={request.request_id} className="border border-[var(--rule)] p-4"><p className="text-sm">{request.raw_text}</p><p className="mt-3 text-xs text-[var(--muted)]">{request.confirmed_classification ? `Classification: ${request.confirmed_classification}` : "Awaiting freelancer classification"}</p></div>) : <p className="text-sm text-[var(--muted)]">No requests recorded yet.</p>}</div></article>;
}

function PolicyView() {
  const [revisionRounds, setRevisionRounds] = useState("2");
  const [preference, setPreference] = useState<OwnerPreference | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  useEffect(() => {
    apiFetch<OwnerPreference>("/preferences")
      .then((value) => {
        setPreference(value);
        if (typeof value.revision_rounds === "number") setRevisionRounds(String(value.revision_rounds));
      })
      .catch((cause) => setMessage(cause instanceof Error ? cause.message : "Could not load preferences."));
  }, []);
  async function save(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const next = await apiFetch<OwnerPreference>("/preferences", { method: "POST", body: JSON.stringify({ revision_rounds: Number(revisionRounds) }) });
      setPreference(next);
      setMessage("Confirmed. New records will stage this as a freelancer policy, never as a client statement.");
    } catch (cause) {
      setMessage(cause instanceof Error ? cause.message : "Could not save the preference.");
    } finally {
      setSaving(false);
    }
  }
  return <section><PageHeading title={pageMeta.policies.title} description={pageMeta.policies.description} /><form onSubmit={save} className="paper-card max-w-2xl rounded-[8px] p-5 sm:p-7"><label className="text-sm font-medium">Default revision rounds for a new draft</label><p className="mt-2 text-sm leading-6 text-[var(--muted)]">This is a freelancer-owned preference. If the client says something different, their sourced statement takes precedence; either way, agreement only happens through the normal client confirmation.</p><input type="number" min="0" max="20" value={revisionRounds} onChange={(event) => setRevisionRounds(event.target.value)} className="focus-ring mt-5 w-28 rounded-[4px] border border-[var(--rule)] bg-[var(--surface-strong)] px-3 py-2" /><div className="mt-6 flex flex-wrap items-center gap-4"><button disabled={saving} className="tap focus-ring rounded-[4px] bg-[var(--accent)] px-4 py-3 text-sm font-medium text-white disabled:opacity-40">{saving ? "Saving..." : "Confirm default policy"}</button>{preference?.status === "CONFIRMED" && <span className="text-sm text-[var(--muted)]">Current: {preference.revision_rounds} rounds</span>}</div>{message && <Message tone={message.startsWith("Confirmed") ? "success" : "error"}>{message}</Message>}</form></section>;
}

function RecordTabs({ runId, active }: { runId: string; active: DetailMode }) {
  const tabs: Array<[DetailMode, string]> = [["sources", "Sources"], ["questions", "Questions"], ["baseline", "Baseline"], ["requests", "Changes"], ["evidence", "Evidence"], ["activity", "Activity"]];
  return <nav className="editorial-scroll -mx-5 overflow-x-auto border-y border-[var(--rule)] px-5 sm:mx-0 sm:px-0"><div className="flex min-w-max gap-1 py-3">{tabs.map(([mode, label]) => <Link key={mode} href={`/records/${runId}/${mode}`} className={`focus-ring rounded-[4px] px-3 py-2 text-sm ${mode === active ? "bg-[var(--accent-soft)] text-[var(--ink)]" : "text-[var(--muted)] hover:text-[var(--ink)]"}`}>{label}</Link>)}</div></nav>;
}

function DetailList({ title, values }: { title: string; values: string[] }) { return <div><h2 className="text-sm font-medium">{title}</h2><ul className="mt-3 space-y-2 text-sm leading-6 text-[var(--muted)]">{values.length ? values.map((value, index) => <li key={`${value}-${index}`}>{value}</li>) : <li>None recorded.</li>}</ul></div>; }
function PageHeading({ title, description, action }: { title: string; description: string; action?: React.ReactNode }) { return <header className="mb-8 flex flex-col justify-between gap-5 border-b border-[var(--rule)] pb-7 sm:flex-row sm:items-end"><div><h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">{title}</h1><p className="mt-4 max-w-2xl text-sm leading-6 text-[var(--muted)]">{description}</p></div>{action}</header>; }
function Status({ value }: { value: string }) { const complete = value === "done"; const failed = value === "failed"; return <span className={`w-fit rounded-[4px] px-2.5 py-1 text-xs ${complete ? "status-ok" : failed ? "text-[var(--danger)]" : "status-warn"}`}>{value}</span>; }
function Message({ children, tone }: { children: React.ReactNode; tone: "error" | "success" | "neutral" }) { return <p className={`mt-5 border p-4 text-sm leading-6 ${tone === "error" ? "border-[var(--danger)]/35 text-[var(--danger)]" : tone === "success" ? "status-ok status-ok-border" : "border-[var(--rule)] text-[var(--muted)]"}`}>{children}</p>; }
function recordTitle(run: OwnerRun) { const candidate = run.ledger?.deliverables?.value?.[0]?.title; return candidate || `Record ${run.run_id.slice(0, 6)}`; }
function detailDescription(mode: DetailMode) { return { sources: "Every client-stated field must point back to the source material.", questions: "Only unresolved work should be sent to the client.", baseline: "Approved versions remain intact. New work takes a separate path.", evidence: "Put the proof beside the promise.", activity: "Events are append-only and ordered by sequence.", requests: "Scope proposals are not decisions until the freelancer confirms them." }[mode]; }
