"""Generate the English voice-over with Gemini TTS.

Reads scripts/beats.json, writes public/audio/<id>.wav (24 kHz mono) plus
src/narration.json with the measured duration of every clip, which is what
the Remotion timeline lays itself out from -- the beat lengths are never
guessed.

    ..\..\..\.venv\Scripts\python.exe scripts\narrate.py
"""

import base64
import json
import os
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(ROOT))
MODEL = os.environ.get("TTS_MODEL", "gemini-3.1-flash-tts-preview")
VOICE = os.environ.get("TTS_VOICE", "Kore")
STYLE = "Read this as a calm, confident product demo narrator, unhurried and clear:"


def api_key():
    with open(os.path.join(REPO, "backend", ".env"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("GEMINI_API_KEY not found in backend/.env")


def synthesize(text, key, attempts=5):
    """Free-tier TTS answers 429 when several clips are asked for in a row,
    so back off and retry instead of losing the clips already generated."""
    for attempt in range(attempts):
        try:
            return _synthesize_once(text, key)
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == attempts - 1:
                raise
            wait = 20 * (attempt + 1)
            print(f"  429 from the API, waiting {wait}s then retrying")
            time.sleep(wait)


def _synthesize_once(text, key):
    body = {
        "contents": [{"parts": [{"text": f"{STYLE} {text}"}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}},
        },
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        payload = json.load(response)
    part = payload["candidates"][0]["content"]["parts"][0]
    inline = part.get("inlineData") or part.get("inline_data")
    return base64.b64decode(inline["data"])


def main():
    key = api_key()
    beats = json.load(open(os.path.join(ROOT, "scripts", "beats.json"), encoding="utf-8"))
    audio_dir = os.path.join(ROOT, "public", "audio")
    os.makedirs(audio_dir, exist_ok=True)
    manifest = []
    for beat in beats:
        wav = os.path.join(audio_dir, f"{beat['id']}.wav")
        pcm = wav + ".pcm"
        # Sudah ada = lewati, supaya menjalankan ulang setelah 429 tidak
        # membakar kuota untuk clip yang sudah jadi.
        if os.path.exists(wav) and "--force" not in sys.argv:
            seconds = float(subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=nw=1:nk=1", wav],
                capture_output=True, text=True, check=True,
            ).stdout.strip())
            manifest.append({**beat, "audio": f"audio/{beat['id']}.wav", "seconds": round(seconds, 2)})
            print(f"{beat['id']:<14} {seconds:6.2f}s  (sudah ada)")
            continue
        with open(pcm, "wb") as f:
            f.write(synthesize(beat["vo"], key))
        subprocess.run(
            ["ffmpeg", "-v", "error", "-f", "s16le", "-ar", "24000", "-ac", "1",
             "-i", pcm, "-y", wav],
            check=True,
        )
        os.remove(pcm)
        seconds = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", wav],
            capture_output=True, text=True, check=True,
        ).stdout.strip())
        manifest.append({**beat, "audio": f"audio/{beat['id']}.wav", "seconds": round(seconds, 2)})
        print(f"{beat['id']:<14} {seconds:6.2f}s")

    total = sum(item["seconds"] for item in manifest)
    print(f"{'TOTAL':<14} {total:6.2f}s  ({total / 60:.2f} min of speech)")
    with open(os.path.join(ROOT, "src", "narration.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


if __name__ == "__main__":
    main()
