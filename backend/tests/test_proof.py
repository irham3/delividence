"""Test Proof Manifest / Acceptance Record — 01-PRD §5 langkah 12, §4.3."""

from app.domain import proof

BASELINE = {
    "version": 1,
    "payload_hash": "sha256:abcd",
    "approved_by": "client",
    "approved_at": "2026-08-26T04:10:00Z",
    "activated_seq": 9,
    "canonical_payload": {
        "criteria": {
            "mobile-breakpoints": {"text": "Renders at 375px.", "text_hash": "sha256:x"},
        }
    },
}


def test_manifest_menyatukan_baseline_status_evidence_dan_decision():
    manifest = proof.build_manifest(
        "deal-1", "Need a landing page.", "en", BASELINE,
        criteria_status={"mobile-breakpoints": "ACCEPTED"},
        evidence_by_criterion={
            "mobile-breakpoints": [{"type": "url", "uri": "https://example.com/shot.png"}]
        },
        latest_decision_by_criterion={
            "mobile-breakpoints": {
                "decision": "ACCEPTED", "actor": "client", "reason": None,
                "created_at": "2026-08-26T05:00:00Z",
            }
        },
    )
    assert manifest["deal_id"] == "deal-1"
    assert manifest["baseline"]["version"] == 1
    crit = manifest["criteria"][0]
    assert crit["criterion_key"] == "mobile-breakpoints"
    assert crit["agreement_source"] == {"baseline_version": 1, "status": "ACCEPTED"}
    assert crit["evidence"][0]["uri"] == "https://example.com/shot.png"
    assert crit["client_decision"]["decision"] == "ACCEPTED"


def test_criterion_tanpa_decision_atau_evidence():
    manifest = proof.build_manifest(
        "deal-1", "brief", "en", BASELINE,
        criteria_status={"mobile-breakpoints": "PENDING"},
        evidence_by_criterion={},
        latest_decision_by_criterion={},
    )
    crit = manifest["criteria"][0]
    assert crit["client_decision"] is None
    assert crit["evidence"] == []


def test_markdown_memuat_baseline_dan_semua_criterion():
    manifest = proof.build_manifest(
        "deal-1", "Need a landing page.", "en", BASELINE,
        criteria_status={"mobile-breakpoints": "ACCEPTED"},
        evidence_by_criterion={
            "mobile-breakpoints": [{"type": "url", "uri": "https://example.com/shot.png"}]
        },
        latest_decision_by_criterion={
            "mobile-breakpoints": {
                "decision": "ACCEPTED", "actor": "client", "reason": None,
                "created_at": "2026-08-26T05:00:00Z",
            }
        },
    )
    md = proof.to_markdown(manifest)
    assert "# Acceptance Record" in md
    assert "mobile-breakpoints" in md
    assert "**ACCEPTED**" in md
    assert "https://example.com/shot.png" in md


def test_markdown_criterion_tanpa_decision_dan_evidence():
    manifest = proof.build_manifest(
        "deal-1", "brief", "en", BASELINE,
        criteria_status={"mobile-breakpoints": "PENDING"},
        evidence_by_criterion={},
        latest_decision_by_criterion={},
    )
    md = proof.to_markdown(manifest)
    assert "Client decision: none yet" in md
    assert "Evidence: none" in md


def test_markdown_menampilkan_reason_saat_ada():
    manifest = proof.build_manifest(
        "deal-1", "brief", "en", BASELINE,
        criteria_status={"mobile-breakpoints": "CHANGES_REQUESTED"},
        evidence_by_criterion={},
        latest_decision_by_criterion={
            "mobile-breakpoints": {
                "decision": "CHANGES_REQUESTED", "actor": "client",
                "reason": "Overlaps at 375px.", "created_at": "2026-08-26T05:00:00Z",
            }
        },
    )
    md = proof.to_markdown(manifest)
    assert "Overlaps at 375px." in md
