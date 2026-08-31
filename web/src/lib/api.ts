export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8080";

// Diisi dari web/src/app/page.tsx lewat setAuthTokenProvider setelah owner
// sign-in -- api.ts sengaja tidak import firebase langsung supaya modul ini
// tetap dipakai apa adanya oleh portal klien (client/[token]/*), yang TIDAK
// pernah butuh Firebase Auth (02 §8: client pakai opaque token, bukan akun).
let getAuthToken: () => Promise<string | null> = async () => null;
let onUnauthorized: (() => void | Promise<void>) | null = null;

export function setAuthTokenProvider(fn: () => Promise<string | null>) {
  getAuthToken = fn;
}

export function setUnauthorizedHandler(fn: (() => void | Promise<void>) | null) {
  onUnauthorized = fn;
}

export type LedgerField<T> = { value: T; state: string };

export type Deliverable = { id: string; title: string };
export type AcceptanceCriterion = {
  deliverable_id: string;
  criterion_key: string;
  text: string;
};

export type Ledger = {
  deliverables?: LedgerField<Deliverable[]>;
  acceptance_criteria?: LedgerField<AcceptanceCriterion[]>;
  in_scope?: LedgerField<string[]>;
  out_of_scope?: LedgerField<string[]>;
  dependencies?: LedgerField<string[]>;
  assumptions?: LedgerField<string[]>;
  unresolved_questions?: LedgerField<string[]>;
  timeline?: { final_deadline?: LedgerField<string> };
  revision_policy?: { rounds_total?: LedgerField<number | "NOT_SET"> };
};

export type Blocker = { field: string; reason: string };
export type Readiness = { ready: boolean; blockers: Blocker[] };

export type ClientView = {
  brief: string;
  output_language: string;
  ledger: Ledger;
  readiness: Readiness;
  payload_hash: string;
};

export type Evidence = {
  evidence_id: string;
  criterion_key: string;
  type: string;
  uri: string;
  caption: string | null;
  uploader_role: string;
  created_at: string;
};

export type ReviewCriterion = {
  criterion_key: string;
  text: string;
  status: string;
  evidence: Evidence[];
};

export type ReviewView = { baseline_version: number; criteria: ReviewCriterion[] };

export type Citation = { ref: string; quote: string };

export type ScopeRequest = {
  request_id: string;
  raw_text: string;
  submitted_by: string;
  confirmed_classification: string | null;
  citations: Citation[];
  // Usulan model (Guardrail) -- bukan keputusan final, hint saja untuk
  // form konfirmasi freelancer di bawah.
  proposed_classification: string | null;
  proposed_citations: Citation[];
  created_at: string;
  decided_at: string | null;
};

export type OwnerRun = {
  run_id: string;
  status: string;
  brief: string;
  output_language: string;
  round: number;
  active_baseline_version?: number;
  created_at: string;
  updated_at: string;
  ledger?: Ledger;
};

export type AuditEvent = {
  event_id: string;
  seq: number;
  type: string;
  actor: string;
  baseline_version: number;
  created_at: string;
  payload: Record<string, unknown>;
};

export type ActiveBaseline = {
  active_version: number;
  baseline: {
    version: number;
    payload_hash: string;
    canonical_payload: {
      // Bentuknya dikunci backend lewat schemas.Deliverable ({id, title}).
      // Sempat diketik `unknown[]`, sehingga `.map(String)` di UI lolos
      // TypeScript dan menampilkan "[object Object]" di layar (ketemu 29 Agu).
      deliverables: Deliverable[];
      in_scope: string[];
      out_of_scope: string[];
      timeline: Record<string, unknown>;
      revision_policy: Record<string, unknown>;
      criteria: Record<string, { text: string; text_hash: string }>;
    };
  };
};

export type OwnerPreference = {
  revision_rounds?: number;
  status: "CONFIRMED" | "NOT_SET";
  confirmed_at?: string;
  updated_at?: string;
};

// Carries the HTTP status so callers can tell a permanent failure (404/403 --
// wrong owner, deleted run) from a transient one (network blip, 5xx) instead
// of treating every fetch failure the same way. Extends Error so existing
// `e instanceof Error` / `e.message` call sites keep working unchanged.
export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function authHeaders(): Promise<Record<string, string>> {
  const token = await getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(await authHeaders()), ...init?.headers },
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    if (res.status === 401 && onUnauthorized) void onUnauthorized();
    throw new ApiError(res.status, `${res.status} ${res.statusText}${detail ? `: ${detail}` : ""}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Untuk endpoint owner yang dulunya dibuka lewat <a href> langsung (View
// JSON/View Markdown) -- anchor navigation tidak bisa membawa header
// Authorization, jadi sekarang fetch manual lalu tampilkan lewat blob URL.
export async function openAuthedInNewTab(path: string): Promise<void> {
  const res = await fetch(`${API}${path}`, { headers: await authHeaders() });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}${detail ? `: ${detail}` : ""}`);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  window.open(url, "_blank", "noreferrer");
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}
