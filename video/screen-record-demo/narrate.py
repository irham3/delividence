import asyncio
import json
import pathlib
import subprocess
import sys

import edge_tts


ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "out"
VOICE_DIR = OUT / "voice"
VOICE_DIR.mkdir(parents=True, exist_ok=True)


async def main():
    items = json.loads((ROOT / "narration.json").read_text(encoding="utf-8"))
    mp3s = []
    for index, item in enumerate(items, start=1):
        target = VOICE_DIR / f"{index:02d}.mp3"
        communicate = edge_tts.Communicate(
            item["text"],
            voice="en-US-GuyNeural",
            rate="+8%",
            pitch="-2Hz",
            volume="+0%",
        )
        await communicate.save(str(target))
        mp3s.append(target)

    concat = OUT / "voice-files.txt"
    concat.write_text(
        "\n".join(f"file '{p.as_posix()}'" for p in mp3s),
        encoding="utf-8",
    )
    combined = OUT / "narration.mp3"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-af",
            "loudnorm=I=-16:LRA=11:TP=-1.5",
            str(combined),
        ],
        check=True,
    )
    print(combined)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"narration failed: {exc}", file=sys.stderr)
        raise
