# ruff: noqa: E501
"""Export the final 1:58 H.264/AAC MP4 with visible and optional captions."""

import json
import subprocess
import sys
from pathlib import Path

out = Path("artifacts/demo")
edit = json.loads(Path("tools/demo/edit.json").read_text())
if "--latest" in sys.argv:
    edit = {"clips": [{"file": (out / "raw-path.txt").read_text().strip(), "start": 0, "end": 118}]}
inputs = []
segments = []
for i, clip in enumerate(edit["clips"]):
    inputs += ["-i", clip["file"]]
    segments.append(
        f"[{i}:v]trim=start={clip['start']}:end={clip['end']},setpts=PTS-STARTPTS,fps=30[v{i}]"
    )
segments.append(
    "".join(f"[v{i}]" for i in range(len(edit["clips"])))
    + f"concat=n={len(edit['clips'])}:v=1:a=0[joined]"
)
video_filter = "drawbox=x=0:y=987:w=iw:h=93:color=0x101820:t=fill,subtitles=artifacts/demo/captions.srt:force_style='FontName=DejaVu Sans,FontSize=10,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101820,BorderStyle=1,Outline=0.5,Shadow=0,MarginV=5,MarginL=50,MarginR=50',fade=t=out:st=117.4:d=0.6"
# Editorial quote repeats the actual successful response in full, without
# changing the app recording or implying a new model request.
if "--latest" not in sys.argv:
    video_filter += (
        ",drawbox=x=70:y=125:w=820:h=295:color=0x101820@0.96:t=fill:enable='between(t,63,75)'"
        ",drawtext=text='RECORDED AI ANSWER / SNAPSHOT 48.56':"
        "x=100:y=153:fontsize=18:fontcolor=0xc3f06b:enable='between(t,63,75)'"
        ",drawtext=textfile=artifacts/demo/recorded-answer.txt:"
        "x=100:y=203:fontsize=25:line_spacing=14:fontcolor=white:enable='between(t,63,75)'"
    )
story = json.loads(Path("tools/demo/story.json").read_text())
video_filter += ",drawbox=x=100:y=0:w=850:h=48:color=0x101820:t=fill:enable='between(t,8,108)'"
for i, chapter in enumerate(story[1:-1], 1):
    textfile = out / f"chapter-{i}.txt"
    textfile.write_text(chapter["label"])
    video_filter += (
        f",drawtext=textfile={textfile}:x=128:y=16:fontsize=17:"
        f"fontcolor=0xc3f06b:enable='between(t,{chapter['start']},{chapter['end']})'"
    )
cmd = [
    "ffmpeg",
    "-y",
    "-v",
    "warning",
    *inputs,
    "-i",
    str(out / "narration.wav"),
    "-i",
    str(out / "captions.srt"),
    "-map",
    "[final]",
    "-map",
    f"{len(edit['clips'])}:a",
    "-map",
    f"{len(edit['clips']) + 1}:0",
    "-filter_complex",
    ";".join(segments + ["[joined]" + video_filter + "[final]"]),
    "-af",
    "afade=t=out:st=117.4:d=0.6",
    "-t",
    "118",
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
    "-c:s",
    "mov_text",
    "-metadata:s:s:0",
    "language=eng",
    "-metadata",
    "title=Touchline — See the game. Understand the story.",
    "-metadata",
    "comment=Working local prototype. Synthetic fictional match, seed 42. AI-synthesized English narration.",
    "-movflags",
    "+faststart",
    str(out / "touchline-demo.mp4"),
]
print("Exporting genuine browser footage from two takes", flush=True)
subprocess.run(cmd, check=True)
probe = json.loads(
    subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(out / "touchline-demo.mp4"),
        ]
    )
)
(out / "media-report.json").write_text(json.dumps(probe, indent=2))
assert float(probe["format"]["duration"]) < 120
assert any(
    s["codec_name"] == "h264" and s["width"] == 1920 and s["height"] == 1080
    for s in probe["streams"]
)
assert any(s["codec_name"] == "aac" for s in probe["streams"])
print("Verified: 1920×1080 H.264 + AAC, under 120 seconds.", flush=True)
