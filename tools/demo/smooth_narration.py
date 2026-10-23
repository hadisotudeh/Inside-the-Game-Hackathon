"""Preserve complete voice takes and normalize the continuous mix uniformly."""

import json
import re
import subprocess
from pathlib import Path

import numpy as np
from scipy.io import wavfile

BASE = Path(".demo-production")
VOICE = BASE / "production/voice"
TEMPO = 0.88
# Reading time after charts, narration, chat and the architecture diagram.
VISUAL_HOLDS = {4: 1.0, 5: 2.0, 6: 2.0, 7: 5.0}


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    return (
        f"{milliseconds // 3600000:02}:{milliseconds // 60000 % 60:02}:"
        f"{milliseconds // 1000 % 60:02},{milliseconds % 1000:03}"
    )


def main():
    timeline = json.loads((BASE / "timeline.json").read_text())
    report = json.loads((BASE / "narration-report.json").read_text())
    clips, chapters = [], []
    cursor, gap = 0.25, 0.08
    rate = None
    for index, chapter in enumerate(timeline["chapters"]):
        sample_rate, data = wavfile.read(VOICE / f"voice-{index}-natural.wav")
        if rate is not None and rate != sample_rate:
            raise ValueError("Voice takes must share a sample rate")
        rate = sample_rate
        samples = data.astype(np.float32)
        if np.issubdtype(data.dtype, np.integer):
            samples /= np.iinfo(data.dtype).max
        if samples.ndim > 1:
            samples = samples.mean(axis=1)
        source_duration = len(samples) / rate
        slowed = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-i",
                str(VOICE / f"voice-{index}-natural.wav"),
                "-af",
                f"atempo={TEMPO}",
                "-f",
                "f32le",
                "-ac",
                "1",
                "-ar",
                str(rate),
                "pipe:1",
            ],
            check=True,
            capture_output=True,
        )
        samples = np.frombuffer(slowed.stdout, dtype=np.float32).copy()
        frame = round(rate * 0.01)
        energy = np.array(
            [
                np.sqrt(np.mean(samples[start : start + frame] ** 2))
                for start in range(0, len(samples), frame)
            ]
        )
        active = np.flatnonzero(energy > 0.004)
        if not len(active):
            raise ValueError(f"Silent chapter {index}")
        # Preserve breathing room and quiet consonants instead of gating each take.
        start, end = 0, len(samples)
        clip = samples[start:end].copy()
        # Fade only the available non-speech edges; never fade an active word.
        fade_in = min(round(rate * 0.05), int(active[0]) * frame)
        fade_out = min(round(rate * 0.05), len(clip) - (int(active[-1]) + 1) * frame)
        fade_out = max(0, fade_out)
        for length, beginning in [(fade_in, True), (fade_out, False)]:
            if length:
                ramp = np.sin(np.linspace(0, np.pi / 2, length)) ** 2
                if beginning:
                    clip[:length] *= ramp
                else:
                    clip[-length:] *= ramp[::-1]
        duration = len(clip) / rate
        hold = VISUAL_HOLDS.get(index, 0)
        chapter.update(start=round(cursor, 4), end=round(cursor + duration + gap + hold, 4))
        clips.append((round(cursor * rate), clip))
        chapters.append(
            {
                "chapter": index,
                "start": chapter["start"],
                "end": chapter["end"],
                "natural_duration": source_duration,
                "source_duration": source_duration,
                "output_duration": duration,
                "trim_start": 0,
                "trim_end": source_duration,
                "tempo_factor": TEMPO,
                "visual_hold_seconds": hold,
                "gain": 1.0,
                "speech_start": int(active[0]) * frame / rate,
                "speech_end": min(len(samples), (int(active[-1]) + 1) * frame) / rate,
            }
        )
        cursor += duration + gap + hold
    timeline["duration"] = round(cursor + 2.0, 4)
    if timeline["duration"] >= 120:
        raise ValueError("Shorten narration or holds to keep the demo below two minutes")
    audio = np.zeros(round(timeline["duration"] * rate), dtype=np.float32)
    for start, clip in clips:
        audio[start : start + len(clip)] += clip
    source = BASE / "smooth-mix.wav"
    wavfile.write(source, rate, audio)
    # Measure the entire narration, then apply one fixed gain without pumping
    # the level independently at every chapter or during pauses.
    measurement = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "info",
            "-i",
            str(source),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    levels, _ = json.JSONDecoder().raw_decode(measurement.stderr[measurement.stderr.rfind("{") :])
    gain_db = min(-16 - float(levels["input_i"]), -1.5 - float(levels["input_tp"]))
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(source),
            "-af",
            f"volume={gain_db}dB",
            "-ar",
            "48000",
            "-t",
            str(timeline["duration"]),
            str(BASE / "narration.wav"),
        ],
        check=True,
    )
    report.update(
        chapters=chapters,
        duration=timeline["duration"],
        timing=(
            "Complete takes retained, including breaths and word endings; 80 ms joins; "
            "up to 50 ms fades confined to non-speech edges; "
            "pitch-preserving 0.88× narration with dedicated visual reading holds."
        ),
        normalization=(
            "One fixed gain measured across the complete narration; "
            "no per-chapter leveling or dynamic gain pumping."
        ),
        global_gain_db=gain_db,
        output=str(BASE / "narration.wav"),
    )
    (BASE / "timeline.json").write_text(json.dumps(timeline, indent=2) + "\n")
    (BASE / "narration-report.json").write_text(json.dumps(report, indent=2) + "\n")
    captions = []
    for chapter, voice in zip(timeline["chapters"], chapters, strict=True):
        sentences = re.split(r"(?<=[.!?])\s+", chapter["text"])
        cursor = chapter["start"] + voice["speech_start"]
        unit = (voice["speech_end"] - voice["speech_start"]) / sum(map(len, sentences))
        for sentence in sentences:
            end = cursor + len(sentence) * unit
            captions.append(
                f"{len(captions) + 1}\n{timestamp(cursor)} --> {timestamp(end - 0.01)}\n{sentence}"
            )
            cursor = end
    (BASE / "captions.srt").write_text("\n\n".join(captions) + "\n")
    print(f"Narration: {timeline['duration']:.2f}s; pitch-preserving {TEMPO}× pace with holds")


if __name__ == "__main__":
    main()
