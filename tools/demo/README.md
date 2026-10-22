# Final demo production

The single approved video is
[artifacts/demo/touchline-demo.mp4](../../artifacts/demo/touchline-demo.mp4),
86.98 seconds at 1920×1080. It uses the owner's reference-conditioned synthetic
voice, with no speech speed-up. Earlier preset-voice versions and their unused
production scripts have been removed.

For ordinary app testing, follow [the judge guide](../../docs/judging.md).
Production tools are optional and separate from the Pipenv runtime dependencies.

## Files and inputs

- `artifacts/demo/timeline.json`: the fixed chapter starts, durations and script.
- `voice_reference.py`: generate local reference-conditioned narration and replace
  the canonical video's audio while copying its compressed picture stream.
- `record_real.py`: record the historical overlay using the fixed timeline.
- `export_real.py`: combine a fresh raw take with the approved narration and captions.
- `title_card.py` and `editorial.css`: opening/closing graphics and camera styling.
- `server.py`: the synthetic judge build on port 8012, run with `pipenv run demo`.

The private voice reference is expected at
`artifacts/demo/production/voice/reference.wav`. The original reference and
voice state are not distributed. A fresh clone can run the application and
play the final video; recreating the narrator requires the owner's private
reference or another speaker's authorized reference. The model and generated
voice are production tools, not an application feature.

## Regenerate narration

Requires Python 3.14, FFmpeg, Pocket TTS 4.0.1 and CPU PyTorch. Install in a separate
local environment, leaving application dependencies unchanged:

```bash
python3.14 -m venv /tmp/touchline-clone-env
/tmp/touchline-clone-env/bin/python -m pip install pocket-tts==4.0.1 --extra-index-url https://download.pytorch.org/whl/cpu
```

Review and accept the model conditions at
<https://huggingface.co/kyutai/pocket-tts>, then authenticate locally:

```bash
HF_HOME=/tmp/touchline-clone-cache /tmp/touchline-clone-env/bin/hf auth login
/tmp/touchline-clone-env/bin/python tools/demo/voice_reference.py
```

The script caches chapters by script/reference hash, writes a natural-speed
preview and narration, validates the muxed video, and atomically replaces
`artifacts/demo/touchline-demo.mp4`. A changed voice or script can require tempo
adjustments to fit the fixed visuals; the published version uses factor 1.0 for
all eight chapters. Review the generated speech before replacing a release.
The source reference, voice state and authentication must stay outside Git.

## Record a new historical take

Requires Google Chrome at `/usr/bin/google-chrome-stable`, FFmpeg with subtitles
support, Playwright, and network access to historical data and Gemini.

```bash
pipenv run python -m pip install --target /tmp/touchline-video-tools playwright==1.64.0
PYTHONPATH=/tmp/touchline-video-tools pipenv run python -m playwright install ffmpeg
pipenv run start
```

With the server on port 8000 and a working Gemini key, use another terminal:

```bash
PYTHONPATH=/tmp/touchline-video-tools pipenv run python tools/demo/check_gemini.py
# Generate approved narration first if narration.wav is absent locally.
TOUCHLINE_DEMO_MICROSOFT=1 PYTHONPATH=/tmp/touchline-video-tools pipenv run python tools/demo/record_real.py
pipenv run python tools/demo/export_real.py
ffmpeg -v error -i artifacts/demo/touchline-demo.mp4 -f null -
```

The recorder produces one continuous take, screenshots, `raw-path.txt` and a
response report. Export trims browser setup, burns captions and validates media
format/duration. It requires a real successful chat response. Re-recording sends
new provider requests; keep source labels and model/service claims accurate.
The scripts overwrite canonical production outputs, so commit the approved
release before a new production run.

## Publication

Only the approved MP4, transcript, captions and reviewable reports are included
in the repository. The approved video is on [YouTube](https://youtu.be/o-lBHqRdArY);
use that URL in the submission form. [Credits](../../docs/assets.md) identify third-party assets and
Kyutai Pocket TTS. These tools do not publish videos or submit the hackathon form.
