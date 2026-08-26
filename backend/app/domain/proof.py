"""Proof Manifest / Acceptance Record (01-PRD §5 langkah 12, §4.3 Acceptance
Matrix) -- menyatukan baseline, evidence, dan keputusan klien per criterion
jadi satu dokumen yang bisa diekspor sebagai JSON atau Markdown.

Fungsi murni: hanya merangkai data yang sudah diambil pemanggil (app/api.py)
dari app/baselines.py, app/evidence.py, dan proyeksi audit event -- tidak
menyentuh Firestore/waktu sendiri.

01 §4.3 melarang mencampur empat lapis Acceptance Matrix jadi satu badge:
agreement source (baseline), artifact integrity (evidence), checks
(deterministic check sungguhan -- di luar cakupan MVP ini, tidak ada yang
benar-benar dijalankan, lihat CATATAN-LANJUTAN.md), dan client decision.
Manifest di sini menjaga keduanya tetap field terpisah, bukan digabung.
"""


def build_manifest(
    deal_id, brief, output_language, baseline, criteria_status,
    evidence_by_criterion, latest_decision_by_criterion,
):
    """`criteria_status`: {criterion_key: effective_status}.
    `evidence_by_criterion`: {criterion_key: [evidence, ...]}.
    `latest_decision_by_criterion`: {criterion_key: decision_dict | None} --
    decision_dict MUST punya decision/actor/reason/created_at kalau ada.
    """
    criteria_out = []
    for key, crit in baseline["canonical_payload"]["criteria"].items():
        decision = latest_decision_by_criterion.get(key)
        criteria_out.append({
            "criterion_key": key,
            "text": crit["text"],
            "text_hash": crit["text_hash"],
            "agreement_source": {
                "baseline_version": baseline["version"],
                "status": criteria_status.get(key),
            },
            "evidence": evidence_by_criterion.get(key, []),
            "client_decision": (
                {
                    "decision": decision["decision"],
                    "actor": decision.get("actor"),
                    "reason": decision.get("reason"),
                    "decided_at": decision.get("created_at"),
                }
                if decision else None
            ),
        })

    return {
        "deal_id": deal_id,
        "brief": brief,
        "output_language": output_language,
        "baseline": {
            "version": baseline["version"],
            "payload_hash": baseline["payload_hash"],
            "approved_by": baseline["approved_by"],
            "approved_at": baseline["approved_at"],
            "activated_seq": baseline["activated_seq"],
        },
        "criteria": criteria_out,
    }


def to_markdown(manifest):
    b = manifest["baseline"]
    lines = [
        "# Acceptance Record",
        "",
        "**Deal:** %s" % manifest["deal_id"],
        "**Baseline version:** %s (approved by %s at %s)" % (b["version"], b["approved_by"], b["approved_at"]),
        "**Payload hash:** `%s`" % b["payload_hash"],
        "",
        "## Criteria",
    ]
    for c in manifest["criteria"]:
        lines += ["", "### %s" % c["criterion_key"], "", c["text"], ""]
        lines.append("- Status: **%s**" % c["agreement_source"]["status"])

        d = c["client_decision"]
        if d:
            lines.append("- Client decision: **%s** (%s, %s)" % (d["decision"], d["actor"], d["decided_at"]))
            if d["reason"]:
                lines.append("  - Reason: %s" % d["reason"])
        else:
            lines.append("- Client decision: none yet")

        if c["evidence"]:
            lines.append("- Evidence:")
            for e in c["evidence"]:
                suffix = " -- %s" % e["caption"] if e.get("caption") else ""
                lines.append("  - [%s] %s%s" % (e["type"], e["uri"], suffix))
        else:
            lines.append("- Evidence: none")

    return "\n".join(lines) + "\n"
