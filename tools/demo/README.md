# Azure demo production

The updated [demo](../../artifacts/demo/touchline-demo.mp4) records the public
Azure site, including opening its URL, historical replay, a real Foundry chat
answer, and the deployed Microsoft stack. The narrator uses Hadi's authorized
private reference and saved voice state. The final narration uses pitch-preserving 0.88× playback and ten seconds of visual reading holds.
The recording uses the app's built-in 15× replay option, zooms in on momentum,
then explains the default narration timeline and chat separately through the
voiceover. It has no side text panel, and the final video stays under two minutes.

## Dependencies

Production dependencies are separate from application runtime dependencies:

```bash
python3 -m venv /tmp/touchline-demo-env
/tmp/touchline-demo-env/bin/pip install pocket-tts==4.0.1 playwright==1.64.0 --extra-index-url https://download.pytorch.org/whl/cpu
```

Requires Chrome at `/usr/bin/google-chrome-stable`, FFmpeg with subtitles,
and Playwright's FFmpeg binary (`python -m playwright install ffmpeg` if absent).
Network access to the hosted app, model downloads and Azure inference is needed.
Re-recording sends a real, usage-billed model question through the live app.

## Voice and timing

Private inputs live at `.demo-production/production/voice/reference.wav` and
`voice-state.safetensors`, with `voice-state.json` identifying reference/model.
The library supports importing an existing saved state. Creating a new state
requires accepting the terms at https://huggingface.co/kyutai/pocket-tts and a
local Hugging Face login; do not store tokens in the repository.

```bash
TOUCHLINE_DEMO_NATURAL_TIMING=1 TOUCHLINE_DEMO_NARRATION_ONLY=1 /tmp/touchline-demo-env/bin/python tools/demo/voice_reference.py
/tmp/touchline-demo-env/bin/python tools/demo/smooth_narration.py
```

This generates narration only, preserves the existing MP4, and creates or reuses the authorized voice takes. The smoothing script preserves complete takes and natural breathing, fades only non-speech edges, uses 80 ms joins, and applies one fixed volume adjustment across the complete narration. It applies pitch-preserving 0.88× playback, adds reading holds for charts, both AI modes and architecture, and updates captions and chapter times. Keep the total under two
minutes and regenerate sentence captions after any script/timing changes.

## Record and export

```bash
TOUCHLINE_DEMO_MICROSOFT=1 /tmp/touchline-demo-env/bin/python tools/demo/record_real.py
.venv/bin/python tools/demo/export_real.py
ffmpeg -v error -i artifacts/demo/touchline-demo.mp4 -f null -
```

The recording uses https://touchline-inside-the-game.azurewebsites.net directly,
not a local proxy. An editorial URL launcher performs a real navigation to that
address. Camera styling and headings aid readability; match data and answers
are unchanged. Check `recording-report.json` for a real Foundry HTTP 200 response,
Agent Framework, all three tools, and no browser errors before exporting.

The previous release is preserved locally under `.demo-production/production/previous-release`.
These scripts replace canonical local demo outputs and do not publish to YouTube.
The latest published demo is available at https://youtu.be/Q1jKv-HsTxo.

Production scripts write temporary files to ignored `.demo-production/`; only the
final MP4 is exported into `artifacts/demo/`. Public transcript and evidence
snapshots are kept in `docs/demo-package/`.
