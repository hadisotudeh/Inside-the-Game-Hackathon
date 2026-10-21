"""Generate conversational narration at its natural pace; derive the edit from it."""

import asyncio
import json
import os
import subprocess
from pathlib import Path

import edge_tts

OUT = Path(os.environ.get("TOUCHLINE_DEMO_OUT", "artifacts/demo-real"))
VOICE = os.environ.get("TOUCHLINE_DEMO_VOICE", "en-US-GuyNeural")
RATE = os.environ.get("TOUCHLINE_DEMO_RATE", "-2%")
PAUSE = float(os.environ.get("TOUCHLINE_DEMO_PAUSE", "0.65"))
STORY = Path(os.environ.get("TOUCHLINE_DEMO_STORY", "tools/demo/story-real.json"))


def duration(path):
    return float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                str(path),
            ]
        )
    )


def stamp(seconds):
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    story = json.loads(STORY.read_text())
    locked_path = OUT / "timeline-recorded.json"
    locked = json.loads(locked_path.read_text()) if locked_path.exists() else None
    cursor = 0.3
    captions = []
    inputs, filters = [], []
    for i, part in enumerate(story):
        if locked:
            cursor = locked["chapters"][i]["start"]
        audio = OUT / f"voice-{i}.mp3"
        metadata = OUT / f"voice-{i}.json"
        if not audio.exists() or audio.stat().st_size < 1000:
            print("Narrating chapter", i, flush=True)
            boundaries = []
            voice = edge_tts.Communicate(
                part["text"],
                VOICE,
                rate=RATE,
                boundary="SentenceBoundary",
            )
            with audio.open("wb") as output:
                async for chunk in voice.stream():
                    if chunk["type"] == "audio":
                        output.write(chunk["data"])
                    elif chunk["type"] == "SentenceBoundary":
                        boundaries.append(chunk)
            metadata.write_text(json.dumps(boundaries, indent=2))
        length = duration(audio)
        part["start"] = round(cursor, 3)
        part["end"] = round(cursor + length + PAUSE, 3)
        if locked:
            part["end"] = locked["chapters"][i]["end"]
            if cursor + length > part["end"]:
                raise RuntimeError(f"Chapter {i} needs shorter text to fit the recorded take.")
        for boundary in json.loads(metadata.read_text()):
            start = cursor + boundary["offset"] / 10_000_000
            end = start + boundary["duration"] / 10_000_000
            captions.append(
                f"{len(captions) + 1}\n{stamp(start)} --> {stamp(end)}\n{boundary['text']}\n"
            )
        inputs += ["-i", str(audio)]
        delay = round(cursor * 1000)
        filters.append(f"[{i}:a]adelay={delay}|{delay}[a{i}]")
        cursor = part["end"]
        print(i, round(length, 2), "seconds; unchanged voice speed", flush=True)
    total = round(cursor + 1.2, 3) if os.environ.get("TOUCHLINE_DEMO_DURATION") == "auto" else 118.0
    if cursor + 0.4 > total:
        raise RuntimeError(f"Narration needs {cursor}s: shorten the script.")
    if total >= 120:
        raise RuntimeError(f"Narration is {total}s: shorten the script, do not accelerate speech.")
    filters.append(
        "".join(f"[a{i}]" for i in range(len(story)))
        + f"amix=inputs={len(story)}:normalize=0,apad,atrim=duration={total},"
        "loudnorm=I=-16:TP=-1.5:LRA=11[out]"
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
    (OUT / "timeline.json").write_text(json.dumps({"duration": total, "chapters": story}, indent=2))
    # The provider occasionally overlaps adjacent sentence boundaries slightly.
    import re

    def seconds(stamp_text):
        hours, minutes, seconds_text = stamp_text.replace(",", ".").split(":")
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds_text)

    for i in range(len(captions) - 1):
        current = re.search(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", captions[i])
        following = re.search(r"(\d{2}:\d{2}:\d{2},\d{3}) -->", captions[i + 1])
        if current and following and seconds(current[2]) >= seconds(following[1]):
            captions[i] = captions[i].replace(current[2], stamp(seconds(following[1]) - 0.01), 1)
    (OUT / "captions.srt").write_text("\n".join(captions))
    (OUT / "narration.txt").write_text("\n\n".join(x["text"] for x in story))
    print("Final natural-paced duration:", total, flush=True)


asyncio.run(main())
