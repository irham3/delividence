"""Production smoke test for Delividence Cloud Run + Firebase Auth.

This script mints a short-lived Firebase custom-token user through IAM
Credentials, exchanges it for a Firebase ID token, then drives the public API
and client-link flow end-to-end. It intentionally never prints tokens.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT = "gen-lang-client-0104798459"
REGION = "asia-southeast2"
API = "https://delividence-api-3jww7h7koq-et.a.run.app"
WEB = "https://delividence.vercel.app"
GCLOUD = r"C:\Users\nameo\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
SERVICE_ACCOUNT = f"delividence-api@{PROJECT}.iam.gserviceaccount.com"


def read_firebase_api_key() -> str:
    for line in (ROOT / "web" / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("NEXT_PUBLIC_FIREBASE_API_KEY="):
            value = line.split("=", 1)[1].strip()
            if value:
                return value
    raise RuntimeError("NEXT_PUBLIC_FIREBASE_API_KEY is missing from web/.env")


def gcloud_access_token() -> str:
    return subprocess.check_output(
        [GCLOUD, "auth", "print-access-token", "--project", PROJECT],
        text=True,
    ).strip()


def request_json(
    method: str,
    url: str,
    *,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 60,
) -> tuple[int, dict[str, Any], dict[str, str]]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req_headers = {"Content-Type": "application/json", **(headers or {})}
    request = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", "replace")
            payload = json.loads(raw) if raw else {}
            return response.status, payload, dict(response.headers.items())
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"raw": raw[:800]}
        return error.code, payload, dict(error.headers.items())


def expect(status: int, want: int, label: str, payload: Any = None) -> None:
    if status != want:
        raise RuntimeError(f"{label}: expected HTTP {want}, got {status}: {payload}")
    print(f"ok: {label}")


def mint_firebase_id_token() -> tuple[str, str, str]:
    api_key = read_firebase_api_key()
    uid = f"prod-smoke-owner-{int(time.time())}"
    now = int(time.time())
    claims = {
        "iss": SERVICE_ACCOUNT,
        "sub": SERVICE_ACCOUNT,
        "aud": "https://identitytoolkit.googleapis.com/google.identity.identitytoolkit.v1.IdentityToolkit",
        "iat": now,
        "exp": now + 3600,
        "uid": uid,
        "claims": {"email": f"{uid}@delividence.test"},
    }
    status, signed, _ = request_json(
        "POST",
        f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/"
        f"{urllib.parse.quote(SERVICE_ACCOUNT, safe='')}:signJwt",
        body={"payload": json.dumps(claims, separators=(",", ":"))},
        headers={"Authorization": f"Bearer {gcloud_access_token()}"},
    )
    expect(status, 200, "IAM signJwt custom token", signed)
    status, firebase, _ = request_json(
        "POST",
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}",
        body={"token": signed["signedJwt"], "returnSecureToken": True},
    )
    expect(status, 200, "Firebase custom token exchange", firebase)
    return uid, firebase["idToken"], api_key


def authed_headers(id_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {id_token}"}


def api_json(method: str, path: str, id_token: str, body: dict[str, Any] | None = None):
    return request_json(method, f"{API}{path}", body=body, headers=authed_headers(id_token), timeout=120)


def poll_run(run_id: str, id_token: str) -> dict[str, Any]:
    deadline = time.time() + 260
    last: dict[str, Any] | None = None
    while time.time() < deadline:
        status, payload, _ = api_json("GET", f"/runs/{run_id}", id_token)
        expect(status, 200, "read run while polling", payload)
        last = payload
        print(f"poll: run={run_id} status={payload.get('status')}")
        if payload.get("status") == "done" and payload.get("ledger"):
            return payload
        if payload.get("status") == "failed":
            raise RuntimeError(f"worker failed run {run_id}: {payload}")
        time.sleep(5)
    raise RuntimeError(f"run did not finish in time: {last}")


def first_criterion_key(run: dict[str, Any]) -> str:
    criteria = run["ledger"]["acceptance_criteria"]["value"]
    if not criteria:
        raise RuntimeError("run has no acceptance criteria")
    return criteria[0]["criterion_key"]


def complete_smoke() -> None:
    uid, id_token, api_key = mint_firebase_id_token()
    try:
        status, session, headers = request_json(
            "POST",
            f"{WEB}/api/auth/session",
            headers=authed_headers(id_token),
        )
        expect(status, 200, "frontend session bridge", session)
        if "delividence_session" not in headers.get("Set-Cookie", ""):
            raise RuntimeError("frontend session bridge did not set delividence_session cookie")
        print("ok: frontend session cookie was issued")

        brief = (
            "Client: Launch the new landing page by September 30, 2026. "
            "Deliver one responsive landing page with hero copy, testimonials, "
            "mobile breakpoint at 375px, and a muted hero video. No paid ads. "
            "Two revision rounds. Client will provide final brand photos today."
        )
        status, created, _ = api_json(
            "POST",
            "/runs",
            id_token,
            {"brief": brief, "output_language": "en"},
        )
        expect(status, 202, "create production run", created)
        run_id = created["run_id"]
        run = poll_run(run_id, id_token)
        criterion_key = first_criterion_key(run)
        print(f"ok: worker/Gemini extraction completed run={run_id} criterion={criterion_key}")

        status, link, _ = api_json(
            "POST",
            f"/runs/{run_id}/client-links",
            id_token,
            {"purpose": "CLARIFICATION"},
        )
        expect(status, 201, "create clarification link", link)
        clarification = link["token"]
        status, client_view, _ = request_json("GET", f"{API}/client/{clarification}")
        expect(status, 200, "public client clarification view", client_view)

        if not client_view["readiness"]["ready"]:
            status, answered, _ = request_json(
                "POST",
                f"{API}/client/{clarification}/answers",
                body={
                    "answers": [
                        {"field": "deliverables", "value": [{"id": "d1", "title": "Landing page"}]},
                        {
                            "field": "acceptance_criteria",
                            "value": [
                                {
                                    "deliverable_id": "d1",
                                    "criterion_key": "mobile-breakpoints",
                                    "text": "Renders at 375px.",
                                }
                            ],
                        },
                        {"field": "out_of_scope", "value": ["No paid ads."]},
                        {"field": "timeline.final_deadline", "value": "2026-09-30"},
                        {"field": "revision_policy.rounds_total", "value": 2},
                    ]
                },
            )
            expect(status, 200, "client answers readiness blockers", answered)
            status, client_view, _ = request_json("GET", f"{API}/client/{clarification}")
            expect(status, 200, "public client clarification view after answers", client_view)

        status, baseline, _ = request_json(
            "POST",
            f"{API}/client/{clarification}/confirm",
            body={"payload_hash": client_view["payload_hash"]},
        )
        expect(status, 200, "client confirms baseline v1", baseline)

        status, citable_refs, _ = api_json("GET", f"/runs/{run_id}/citable-refs", id_token)
        expect(status, 200, "read citable refs", citable_refs)
        citation_ref, citation_text = next(iter(citable_refs.items()))

        status, request, _ = api_json(
            "POST",
            f"/runs/{run_id}/requests",
            id_token,
            {"raw_text": "Please also create three vertical TikTok visuals.", "submitted_by": "freelancer"},
        )
        expect(status, 201, "log post-baseline request with Guardrail", request)
        print(
            "ok: guardrail proposal="
            + str(request.get("proposed_classification"))
            + " citations="
            + str(len(request.get("proposed_citations") or []))
        )
        request_id = request["request_id"]

        status, classified, _ = api_json(
            "POST",
            f"/runs/{run_id}/requests/{request_id}/classify",
            id_token,
            {
                "classification": "CHANGE_REQUEST",
                "citations": [{"ref": citation_ref, "quote": citation_text}],
            },
        )
        expect(status, 200, "freelancer confirms request classification", classified)

        current = run["ledger"]["acceptance_criteria"]["value"]
        next_criteria = [
            *current,
            {
                "deliverable_id": current[0]["deliverable_id"],
                "criterion_key": "tiktok-verticals",
                "text": "Three vertical TikTok visuals at 1080x1920.",
            },
        ]
        status, proposal, _ = api_json(
            "POST",
            f"/runs/{run_id}/change-proposal",
            id_token,
            {"answers": [{"field": "acceptance_criteria", "value": next_criteria}]},
        )
        expect(status, 200, "stage change proposal", proposal)

        status, link2, _ = api_json(
            "POST",
            f"/runs/{run_id}/client-links",
            id_token,
            {"purpose": "CLARIFICATION"},
        )
        expect(status, 201, "create v2 clarification link", link2)
        status, v2_view, _ = request_json("GET", f"{API}/client/{link2['token']}")
        expect(status, 200, "public client v2 view", v2_view)
        status, baseline2, _ = request_json(
            "POST",
            f"{API}/client/{link2['token']}/confirm",
            body={"payload_hash": v2_view["payload_hash"]},
        )
        expect(status, 200, "client confirms baseline v2", baseline2)

        status, evidence, _ = api_json(
            "POST",
            f"/runs/{run_id}/evidence",
            id_token,
            {
                "criterion_key": criterion_key,
                "type": "url",
                "uri": "https://demo.delividence.test/mobile-proof.png",
                "caption": "375px browser capture",
            },
        )
        expect(status, 201, "attach delivery evidence", evidence)

        status, review_link, _ = api_json(
            "POST",
            f"/runs/{run_id}/client-links",
            id_token,
            {"purpose": "DELIVERY_REVIEW"},
        )
        expect(status, 201, "create delivery review link", review_link)
        status, review_view, _ = request_json("GET", f"{API}/client/{review_link['token']}/review")
        expect(status, 200, "public delivery review view", review_view)
        decisions = [
            {"criterion_key": item["criterion_key"], "decision": "ACCEPTED"}
            for item in review_view["criteria"]
        ]
        status, review_submit, _ = request_json(
            "POST",
            f"{API}/client/{review_link['token']}/review",
            body={"decisions": decisions},
        )
        expect(status, 200, "client submits delivery review", review_submit)

        status, proof, _ = api_json("GET", f"/runs/{run_id}/proof", id_token)
        expect(status, 200, "export proof JSON", proof)
        if proof["baseline"]["version"] != 2:
            raise RuntimeError(f"expected proof baseline v2, got {proof['baseline']['version']}")
        if not proof["criteria"]:
            raise RuntimeError("proof contains no criteria")
        print(f"PASS production_e2e run_id={run_id} uid={uid}")
    finally:
        status, _, _ = request_json(
            "POST",
            f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={api_key}",
            body={"idToken": id_token},
        )
        if status == 200:
            print(f"ok: deleted temporary Firebase user uid={uid}")
        else:
            print(f"warn: could not delete temporary Firebase user uid={uid} status={status}")


if __name__ == "__main__":
    try:
        complete_smoke()
    except Exception as exc:
        print(f"FAIL production_e2e: {exc}", file=sys.stderr)
        raise
