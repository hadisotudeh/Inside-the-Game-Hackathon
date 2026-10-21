# American male narration for the next Touchline take

`voice-preview.mp3` is a 21-second preview. `narration.wav` contains the full
1:58 audio timeline, including natural pauses and closing-card hold.

Voice: `en-US-GuyNeural`, rate -2%, with no post-generation speech speed-up.
The aim is a calm, conversational American delivery. This is a standard
synthetic voice and does not guarantee a non-native accent.

The clean script is `tools/demo/story-clean.json`. It describes a successful
AI answer and must be paired with a new recording that actually obtains one.
The existing historical-match MP4 has not been replaced with this audio.

Suggested retry: October 22, 2026, at 10:35 a.m. Tehran time, shortly after
the documented daily reset (midnight Pacific, 10:30 a.m. Tehran on that date).
The prior app error does not identify a specific quota dimension; a daily
reset is not a guarantee of model availability. Verify one real answer before
recording. No automated retry or scheduled task has been created.

Once the app on port 8000 can answer:

```bash
TOUCHLINE_DEMO_OUT=artifacts/demo-american PYTHONPATH=/tmp/touchline-video-tools .venv/bin/python tools/demo/record_real.py
TOUCHLINE_DEMO_OUT=artifacts/demo-american .venv/bin/python tools/demo/export_real.py
```

Check `recording-report.json` for a real successful AI response before using
this clean narration in a final exported demo.
