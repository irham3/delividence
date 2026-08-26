import pytest

from app import config


@pytest.fixture(autouse=True)
def isolated_local_state(tmp_path, monkeypatch):
    """Setiap test dapat state lokal sendiri, dan tidak pernah menyentuh cloud."""
    monkeypatch.setattr(config, "LOCAL", True)
    monkeypatch.setattr(config, "LOCAL_DATA_DIR", str(tmp_path))


@pytest.fixture
def published(monkeypatch):
    """Tangkap pesan yang dipublikasikan, tanpa memanggil worker sungguhan."""
    from app import queue

    sent = []
    monkeypatch.setattr(queue, "publish", lambda message: sent.append(message))
    return sent


@pytest.fixture(autouse=True)
def fake_owner():
    """Semua test lain menganggap sudah login sebagai satu owner tetap --
    verifikasi Firebase ID token sungguhan (app/auth.py) diuji terpisah di
    tests/test_auth.py, bukan di sini. Firestore/HTTP asli tidak pernah
    dipanggil (dependency override langsung, bukan token asli)."""
    from app.api import app as api_app
    from app import auth

    api_app.dependency_overrides[auth.require_owner] = lambda: "test-owner-1"
    yield
    api_app.dependency_overrides.pop(auth.require_owner, None)


@pytest.fixture(autouse=True)
def stub_extraction(monkeypatch):
    """Test lewat worker push handler TIDAK memanggil Gemini sungguhan --
    supaya test suite cepat, deterministik, dan tidak butuh GEMINI_API_KEY.
    Wiring worker.run_extraction ke Gemini sungguhan diverifikasi manual
    lewat uvicorn (lihat CATATAN-LANJUTAN.md), bukan di sini."""
    from app import worker

    async def _stub(run_id, brief):
        return None

    monkeypatch.setattr(worker, "run_extraction", _stub)


@pytest.fixture(autouse=True)
def stub_guardrail_agent(monkeypatch):
    """Test lewat POST /runs/{id}/requests TIDAK memanggil Gemini sungguhan
    -- sama alasan dan pola persis dengan stub_extraction di atas."""
    from app import api

    async def _stub(raw_text, text_by_ref):
        return None

    monkeypatch.setattr(api, "propose_scope_classification", _stub)
