"""Make a local reference-conditioned narration and retain the approved visuals."""

import hashlib
import json
import os
import subprocess
from pathlib import Path

os.environ.setdefault("HF_HOME", "/tmp/touchline-clone-cache")
os.environ.setdefault("TORCH_HOME", "/tmp/touchline-clone-cache/torch")

import scipy.io.wavfile
import torch
from pocket_tts import TTSModel, export_model_state

BASE = Path("artifacts/demo")
OUT = BASE / "production/voice"
REFERENCE = OUT / "reference.wav"
VIDEO = BASE / "touchline-demo.mp4"
MODEL = "english_2026-09_2"


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def duration(path):
    return float(
        run(
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        )
    )


def picture_hash(path):
    return run(
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(path),
        "-map",
        "0:v:0",
        "-c",
        "copy",
        "-f",
        "hash",
        "-hash",
        "sha256",
        "-",
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    timeline = json.loads((BASE / "timeline.json").read_text())
    reference_hash = hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
    print("Loading local voice-cloning model", MODEL, flush=True)
    torch.set_num_threads(2)
    torch.manual_seed(42)
    model = TTSModel.load_model(language=MODEL)
    if not model.has_voice_cloning:
        raise SystemExit(
            "Voice-cloning weights require access: accept the terms at "
            "https://huggingface.co/kyutai/pocket-tts, then run "
            "HF_HOME=/tmp/touchline-clone-cache "
            "/tmp/touchline-clone-env/bin/hf auth login in your terminal."
        )
    state_path = OUT / "voice-state.safetensors"
    state_meta = OUT / "voice-state.json"
    signature = {"reference_sha256": reference_hash, "model": MODEL}
    if (
        state_path.exists()
        and state_meta.exists()
        and json.loads(state_meta.read_text()) == signature
    ):
        state = model.get_state_for_audio_prompt(state_path)
    else:
        state = model.get_state_for_audio_prompt(REFERENCE)
        export_model_state(state, state_path)
        state_meta.write_text(json.dumps(signature, indent=2) + "\n")
    inputs, filters, chapters = [], [], []
    for i, part in enumerate(timeline["chapters"]):
        path = OUT / f"voice-{i}-natural.wav"
        metadata = OUT / f"voice-{i}.json"
        text_hash = hashlib.sha256(part["text"].encode()).hexdigest()
        cache_key = {**signature, "text_sha256": text_hash}
        cached = json.loads(metadata.read_text()) if metadata.exists() else {}
        if not path.exists() or cached.get("cache_key") != cache_key:
            print(f"Generating chapter {i + 1}/{len(timeline['chapters'])}", flush=True)
            audio = model.generate_audio(state, part["text"])
            scipy.io.wavfile.write(path, model.sample_rate, audio.detach().cpu().numpy())
            metadata.write_text(json.dumps({"cache_key": cache_key}, indent=2) + "\n")
        if i == 0:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-v",
                    "error",
                    "-i",
                    str(path),
                    "-af",
                    "loudnorm=I=-16:TP=-1.5:LRA=11",
                    str(OUT / "voice-preview.wav"),
                ],
                check=True,
            )
            print("Natural-speed preview ready:", OUT / "voice-preview.wav", flush=True)
        natural_duration = duration(path)
        budget = part["end"] - part["start"] - 0.12
        tempo = max(1.0, natural_duration / budget)
        if tempo > 2:
            raise RuntimeError(
                f"Chapter {i}: cannot fit this delivery without excessive compression"
            )
        # Copy video exactly; retain pitch while fitting speech to the recorded chapter.
        delay = round(part["start"] * 1000)
        inputs.extend(["-i", str(path)])
        filters.append(f"[{i}:a]atempo={tempo:.8f},adelay={delay}|{delay}[a{i}]")
        chapters.append(
            {
                "chapter": i,
                "start": part["start"],
                "end": part["end"],
                "natural_duration": natural_duration,
                "tempo_factor": tempo,
            }
        )
        print(
            f"Chapter {i + 1}: natural {natural_duration:.2f}s; fit factor {tempo:.3f}", flush=True
        )
    total = timeline["duration"]
    filters.append(
        "".join(f"[a{i}]" for i in range(len(chapters)))
        + f"amix=inputs={len(chapters)}:normalize=0,apad,atrim=duration={total},"
        "loudnorm=I=-16:TP=-1.5:LRA=11[out]"
    )
    narration = OUT / "narration.wav"
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
            str(narration),
        ],
        check=True,
    )
    final = OUT / "touchline-demo.render.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(VIDEO),
            "-i",
            str(narration),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-af",
            f"afade=t=out:st={total - 0.6}:d=0.6",
            "-t",
            str(total),
            "-metadata:s:a:0",
            "language=eng",
            "-metadata",
            "comment=Synthetic narration conditioned on the owner's supplied voice sample.",
            "-movflags",
            "+faststart",
            str(final),
        ],
        check=True,
    )
    original_hash = picture_hash(VIDEO)
    actual_hash = picture_hash(final)
    if actual_hash != original_hash:
        raise RuntimeError("Picture stream changed")
    if abs(duration(final) - total) > 0.1:
        raise RuntimeError("Final duration changed")
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(final),
            "-f",
            "null",
            "-",
        ],
        check=True,
    )
    report = {
        "model": MODEL,
        "reference_sha256": reference_hash,
        "reference_source_offset_seconds": 43.9,
        "reference_duration_seconds": 15.8,
        "generation": "Local synthetic speech from the reference; similarity needs owner review.",
        "output": str(final),
        "duration": duration(final),
        "video_matches_original": True,
        "video_stream_sha256": actual_hash,
        "decode_check": "passed",
        "chapters": chapters,
        "timing": "Pitch-preserving tempo adjustment to chapter slots; captions unchanged.",
    }
    final.replace(VIDEO)
    report["output"] = str(VIDEO)
    (BASE / "narration-report.json").write_text(json.dumps(report, indent=2) + "\n")
    import shutil

    shutil.copy2(narration, BASE / "narration.wav")
    shutil.copy2(OUT / "voice-preview.wav", BASE / "voice-preview.wav")
    print("Ready:", VIDEO, flush=True)


if __name__ == "__main__":
    main()
