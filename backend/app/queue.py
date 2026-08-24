"""Publikasi pekerjaan ke worker.

Produksi: Pub/Sub. Lokal: HTTP langsung ke worker dengan bentuk envelope yang
sama persis seperti push subscription, supaya handler yang diuji lokal adalah
handler yang sama yang dipakai di produksi.
"""

import base64
import json
import threading

from app import config

_publisher = None


def _topic_path():
    global _publisher
    if _publisher is None:
        from google.cloud import pubsub_v1

        _publisher = pubsub_v1.PublisherClient()
    return _publisher, _publisher.topic_path(config.PROJECT_ID, config.PUBSUB_TOPIC)


def _post_local(envelope):
    import httpx

    try:
        httpx.post(config.WORKER_URL + "/pubsub/push", json=envelope, timeout=30.0)
    except Exception:
        # Mode lokal saja. Di produksi Pub/Sub yang menangani retry & dead-letter.
        pass


def publish(message):
    data = json.dumps(message).encode("utf-8")

    if config.LOCAL:
        envelope = {
            "message": {
                "data": base64.b64encode(data).decode("ascii"),
                "messageId": "local-%s-%s" % (message.get("run_id"), message.get("round")),
            },
            "subscription": "local",
        }
        # Thread supaya API tidak menunggu worker selesai — eksekusi tetap
        # terpisah dari request, sama seperti di produksi.
        threading.Thread(target=_post_local, args=(envelope,), daemon=True).start()
        return envelope["message"]["messageId"]

    publisher, topic = _topic_path()
    return publisher.publish(topic, data).result(timeout=30)
