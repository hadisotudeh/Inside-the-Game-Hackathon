import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts

OUT = Path("artifacts/demo")


async def main():
    story = json.loads(Path("tools/demo/story.json").read_text())
    for i, s in enumerate(story):
        dest = OUT / f"voice-{i}.mp3"
        if dest.exists() and dest.stat().st_size > 1000:
            continue
        print("Generating narration", i, flush=True)
        await edge_tts.Communicate(s["text"], "en-GB-RyanNeural", rate="+3%").save(str(dest))
    filters = []
    inputs = []
    for i, s in enumerate(story):
        src = OUT / f"voice-{i}.mp3"
        duration = float(
            subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "csv=p=0",
                    str(src),
                ]
            )
        )
        slot = s["end"] - s["start"]
        tempo = max(0.88, duration / (slot - 0.65))
        inputs += ["-i", str(src)]
        filters.append(
            f"[{i}:a]atempo={tempo:.5f},apad,atrim=duration={slot},asetpts=PTS-STARTPTS[a{i}]"
        )
        print(i, round(duration, 2), "seconds; tempo", round(tempo, 2), flush=True)
    filters.append(
        "".join(f"[a{i}]" for i in range(len(story)))
        + f"concat=n={len(story)}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[out]"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            *inputs,
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-ar",
            "48000",
            str(OUT / "narration.wav"),
        ],
        check=True,
    )
    # Editable sidecar captions, split into short sentences within each chapter.
    import re

    captions = []

    def stamp(t):
        ms = round(t * 1000)
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

    for s in story:
        sentences = re.split(r"(?<=[.!?])\s+", s["text"])
        words = sum(len(x.split()) for x in sentences)
        t = s["start"]
        for sentence in sentences:
            end = t + (s["end"] - s["start"] - 0.3) * len(sentence.split()) / words
            captions.append(f"{len(captions) + 1}\n{stamp(t)} --> {stamp(end)}\n{sentence}\n")
            t = end
    (OUT / "captions.srt").write_text("\n".join(captions))
    (OUT / "narration.txt").write_text("\n\n".join(s["text"] for s in story))


asyncio.run(main())
