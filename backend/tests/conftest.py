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
