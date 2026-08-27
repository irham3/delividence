"""Tooling lokal-only: tarik pesan dari pull subscription Pub/Sub produksi
dan teruskan ke worker lokal (http://127.0.0.1:8081/pubsub/push) dengan
envelope yang sama persis dengan push subscription asli.

Dipakai HANYA kalau GOOGLE_CLOUD_PROJECT di .env diisi (backend lokal
nyambung ke Firestore/Pub-Sub produksi sungguhan) -- subscription push yang
sudah ada (delividence-runs-push) tetap mengirim ke Cloud Run worker seperti
biasa; script ini menambah jalur KEDUA lewat subscription pull terpisah
supaya worker lokal juga kebagian salinan job yang sama. Job akan diproses
DUA KALI (Cloud Run + lokal) -- ini disengaja, bukan bug.

Bukan bagian dari aplikasi (tidak dipanggil dari mana pun di app/), dan
tidak perlu dijalankan sama sekali kalau GOOGLE_CLOUD_PROJECT dikosongkan.

Pemakaian:
    ..\.venv\Scripts\python.exe local_pubsub_forwarder.py
"""

import base64
import json
import os
import time

import requests
from google.cloud import pubsub_v1

from app import config

# Tiap developer pakai subscription pull sendiri (SUBSCRIPTION_ID beda-beda)
# supaya tidak rebutan pesan -- subscription pull load-balance pesan antar
# consumer yang narik dari subscription YANG SAMA, jadi dua orang di
# subscription yang sama akan berbagi (bukan dapat salinan masing-masing).
SUBSCRIPTION_ID = os.environ.get("LOCAL_PULL_SUBSCRIPTION_ID", "delividence-runs-local-pull")
WORKER_PUSH_URL = "http://127.0.0.1:8081/pubsub/push"


def _ensure_subscription(subscriber, project_id, topic_id):
    sub_path = subscriber.subscription_path(project_id, SUBSCRIPTION_ID)
    try:
        subscriber.get_subscription(subscription=sub_path)
        print(f"subscription {SUBSCRIPTION_ID} sudah ada")
    except Exception:
        topic_path = subscriber.topic_path(project_id, topic_id) if hasattr(
            subscriber, "topic_path"
        ) else f"projects/{project_id}/topics/{topic_id}"
        subscriber.create_subscription(name=sub_path, topic=topic_path)
        print(f"subscription {SUBSCRIPTION_ID} dibuat")
    return sub_path


def forward(message):
    envelope = {
        "message": {
            "data": base64.b64encode(message.data).decode("ascii"),
            "messageId": message.message_id,
        }
    }
    try:
        resp = requests.post(WORKER_PUSH_URL, json=envelope, timeout=60)
        resp.raise_for_status()
        message.ack()
        print(f"diteruskan ke worker lokal, status {resp.status_code}")
    except Exception as e:
        print(f"gagal diteruskan, nack: {e}")
        message.nack()


def main():
    if not config.PROJECT_ID:
        raise SystemExit(
            "GOOGLE_CLOUD_PROJECT kosong di .env -- script ini cuma untuk mode "
            "nyambung ke Pub/Sub produksi. Tidak perlu dijalankan untuk mode LOCAL biasa."
        )

    subscriber = pubsub_v1.SubscriberClient()
    sub_path = _ensure_subscription(subscriber, config.PROJECT_ID, config.PUBSUB_TOPIC)

    print(f"mendengarkan {sub_path} -> forward ke {WORKER_PUSH_URL}")
    streaming_pull = subscriber.subscribe(sub_path, callback=forward)
    try:
        streaming_pull.result()
    except KeyboardInterrupt:
        streaming_pull.cancel()
        streaming_pull.result()


if __name__ == "__main__":
    main()
