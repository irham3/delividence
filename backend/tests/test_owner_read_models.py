"""Read-model endpoints used by the non-workspace owner pages.

The pages must read the same owner-isolated facts as the main workspace; they
cannot silently infer a record from browser state or expose another owner’s
run just because it exists in the store.
"""

from fastapi.testclient import TestClient

from app import config, store
from app.api import app as api_app

api = TestClient(api_app)


def test_list_runs_firestore_tidak_menuntut_composite_index(monkeypatch):
    """Ketemu 29 Agu di PRODUCTION: `list_runs` sempat memakai
    `.where("owner_id") .order_by("updated_at")`, yang di Firestore menuntut
    composite index. Index itu tidak ada, jadi query gagal total
    (FailedPrecondition 400) dan SEMUA halaman daftar (/records, /sources,
    /review, /activity) mati dengan "Failed to fetch" di browser. Test suite
    tidak menangkapnya karena semua test jalan di mode LOCAL (file JSON),
    tidak pernah menyentuh Firestore sungguhan.

    Test ini menjaga jalur Firestore-nya: urutan dikerjakan di Python, dan
    `order_by` tidak boleh dipanggil lagi -- kalau dipanggil, deployment baru
    (termasuk juri di project sendiri) akan patah lagi dengan cara yang sama.
    """
    calls = []

    class _FakeQuery:
        def where(self, *args, **kwargs):
            calls.append("where")
            return self

        def order_by(self, *args, **kwargs):  # pragma: no cover - harus tidak terpanggil
            calls.append("order_by")
            return self

        def stream(self):
            return [
                _FakeDoc({"run_id": "lama", "owner_id": "o1", "updated_at": "2026-08-01T00:00:00Z"}),
                _FakeDoc({"run_id": "baru", "owner_id": "o1", "updated_at": "2026-08-29T00:00:00Z"}),
            ]

    class _FakeDoc:
        def __init__(self, data):
            self._data = data

        def to_dict(self):
            return self._data

    class _FakeClient:
        def collection(self, name):
            calls.append("collection:%s" % name)
            return _FakeQuery()

    monkeypatch.setattr(config, "LOCAL", False)
    monkeypatch.setattr(store, "_client", lambda: _FakeClient())

    items = store.list_runs("o1")

    assert "order_by" not in calls, "list_runs tidak boleh memakai order_by Firestore (butuh composite index)"
    # Tetap terbaru-dulu, diurutkan di Python.
    assert [item["run_id"] for item in items] == ["baru", "lama"]


def test_run_index_is_owner_scoped_and_activity_is_per_run(published):
    mine = api.post("/runs", json={"brief": "My client material."}).json()["run_id"]
    store.create_run("foreign-run", "another-owner", "Private material.", "en")

    listing = api.get("/runs")
    assert listing.status_code == 200
    assert [item["run_id"] for item in listing.json()["items"]] == [mine]

    activity = api.get(f"/runs/{mine}/activity")
    assert activity.status_code == 200
    assert [event["type"] for event in activity.json()["items"]] == [
        "DEAL_CREATED",
        "ARTIFACT_ADDED",
    ]


def test_active_baseline_read_model_returns_confirmed_version(published):
    run_id = api.post("/runs", json={"brief": "Need a landing page."}).json()["run_id"]
    token = api.post(f"/runs/{run_id}/client-links").json()["token"]
    answers = [
        {"field": "deliverables", "value": [{"id": "d1", "title": "Landing page"}]},
        {"field": "acceptance_criteria", "value": [{"deliverable_id": "d1", "criterion_key": "mobile", "text": "Renders at 375px."}]},
        {"field": "out_of_scope", "value": ["No paid ads."]},
        {"field": "timeline.final_deadline", "value": "2026-08-31"},
        {"field": "revision_policy.rounds_total", "value": 2},
    ]
    api.post(f"/client/{token}/answers", json={"answers": answers})
    payload_hash = api.get(f"/client/{token}").json()["payload_hash"]
    assert api.post(f"/client/{token}/confirm", json={"payload_hash": payload_hash}).status_code == 200

    response = api.get(f"/runs/{run_id}/baseline")
    assert response.status_code == 200
    body = response.json()
    assert body["active_version"] == 1
    assert body["baseline"]["canonical_payload"]["criteria"]["mobile"]["text"] == "Renders at 375px."
