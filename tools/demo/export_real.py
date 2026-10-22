# ruff: noqa: E501
"""Export the historical case-study take, keeping the natural voice timing."""

import json
import os
import subprocess
from pathlib import Path

OUT = Path(os.environ.get("TOUCHLINE_DEMO_OUT", "artifacts/demo"))
timeline = json.loads((OUT / "timeline.json").read_text())
total = timeline["duration"]
raw = Path((OUT / "raw-path.txt").read_text().strip())
raw_duration = float(
    subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(raw),
        ]
    )
)
# Remove only browser setup time; retain continuous replay and all real answers.
trim = max(0, raw_duration - total)
vf = (
    "drawbox=x=0:y=987:w=iw:h=93:color=0x101820:t=fill,"
    f"subtitles={OUT}/captions.srt:force_style='FontName=DejaVu Sans,"
    "FontSize=10,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101820,"
    "BorderStyle=1,Outline=0.5,Shadow=0,MarginV=5,MarginL=50,MarginR=50'"
)
for i, part in enumerate(timeline["chapters"][1:-1], 1):
    label = OUT / f"chapter-{i}.txt"
    label.write_text(part["label"])
    enable = f"between(t,{part['start']},{part['end']})"
    vf += (
        f",drawbox=x=100:y=0:w=800:h=48:color=0x101820:t=fill:enable='{enable}'"
        f",drawtext=textfile={label}:x=128:y=16:fontsize=16:fontcolor=0xc3f06b:enable='{enable}'"
    )
# Label the recorded provider outcome as an editorial annotation. This is
# taken from the real response report, not an invented UI answer.
request_report = json.loads((OUT / "recording-report.json").read_text())
if not any(item["status"] == 200 for item in request_report["chat_responses"]):
    raise RuntimeError("The narration requires a recorded successful AI answer; retry later.")
if any(item["status"] == 429 for item in request_report["chat_responses"]):
    error_start = timeline["chapters"][6]["start"] + 6
    error_end = timeline["chapters"][6]["end"] - 1
    enable = f"between(t,{error_start},{error_end})"
    vf += (
        f",drawbox=x=70:y=125:w=780:h=195:color=0x101820@0.97:t=fill:enable='{enable}'"
        f",drawtext=text='RECORDED API RESPONSE':x=100:y=151:fontsize=18:"
        f"fontcolor=0xc3f06b:enable='{enable}'"
        f",drawtext=text='Gemini returned HTTP 429 - quota exhausted.':x=100:y=198:"
        f"fontsize=27:fontcolor=white:enable='{enable}'"
        f",drawtext=text='Replay and analytics continue.':x=100:y=249:fontsize=25:"
        f"fontcolor=white:enable='{enable}'"
    )
vf += f",fade=t=out:st={total - 0.6}:d=0.6"
final = OUT / "touchline-demo.mp4"
subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-v",
        "warning",
        "-ss",
        str(trim),
        "-i",
        str(raw),
        "-i",
        str(OUT / "narration.wav"),
        "-map",
        "0:v",
        "-map",
        "1:a",
        "-vf",
        vf,
        "-af",
        f"afade=t=out:st={total - 0.6}:d=0.6",
        "-t",
        str(total),
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "19",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-metadata",
        "title=Touchline — A Premier League event-data case study",
        "-metadata",
        "comment=Recorded from localhost:8000/overlay. Historical Chelsea v Arsenal replay. StatsBomb Open Data. Synthetic English narration at natural pace. No broadcast match footage.",
        "-movflags",
        "+faststart",
        str(final),
    ],
    check=True,
)
report = json.loads(
    subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(final),
        ]
    )
)
assert float(report["format"]["duration"]) < 120
assert any(
    s["codec_name"] == "h264" and s["width"] == 1920 and s["height"] == 1080
    for s in report["streams"]
)
assert any(s["codec_name"] == "aac" for s in report["streams"])
(OUT / "media-report.json").write_text(json.dumps(report, indent=2))
print("Exported:", final, "duration:", report["format"]["duration"], flush=True)
