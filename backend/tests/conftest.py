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
def stub_extraction(monkeypatch):
    """Test lewat worker push handler TIDAK memanggil Gemini sungguhan --
    supaya test suite cepat, deterministik, dan tidak butuh GEMINI_API_KEY.
    Wiring worker.run_extraction ke Gemini sungguhan diverifikasi manual
    lewat uvicorn (lihat CATATAN-LANJUTAN.md), bukan di sini."""
    from app import worker

    async def _stub(run_id, brief):
        return None

    monkeypatch.setattr(worker, "run_extraction", _stub)
