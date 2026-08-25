export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8080";

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
  out_of_scope?: LedgerField<string[]>;
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
  created_at: string;
  decided_at: string | null;
};

export type ProofManifest = {
  criteria: { criterion_key: string; text: string }[];
};

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}${detail ? `: ${detail}` : ""}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}
