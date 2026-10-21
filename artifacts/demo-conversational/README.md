# Touchline — conversational narration revision

Voice: en-US-AndrewMultilingualNeural, American male, +8% provider delivery
rate, 0.2-second chapter pauses. Synthetic narration; no post-generation
audio speed changes. Conversational script: tools/demo/story-conversational.json.
The final duration follows the speech instead of padding to 118 seconds.

Files:
- voice-preview.mp3: first 20 seconds for quick voice review.
- touchline-demo-real-match.mp4: complete demo with one set of burned-in captions; no selectable subtitle track.
- recording-report.json: real UI errors, Gemini status, and replay clocks.

Microsoft Agent Framework, the optional Foundry adapter and proposed Azure
integrations remain highlighted. The opening retains the white design,
hackathon branding and bold AI text. The script reports the quota failure
seen in the preceding real Gemini checks; this recording sends a fresh question.

Reproduce:

```bash
TOUCHLINE_DEMO_OUT=artifacts/demo-conversational TOUCHLINE_DEMO_STORY=tools/demo/story-conversational.json TOUCHLINE_DEMO_VOICE=en-US-AndrewMultilingualNeural TOUCHLINE_DEMO_RATE=+8% TOUCHLINE_DEMO_PAUSE=0.2 TOUCHLINE_DEMO_DURATION=auto PYTHONPATH=/tmp/touchline-video-tools .venv/bin/python tools/demo/voice_real.py
TOUCHLINE_DEMO_OUT=artifacts/demo-conversational TOUCHLINE_DEMO_MICROSOFT=1 PYTHONPATH=/tmp/touchline-video-tools .venv/bin/python tools/demo/record_real.py
TOUCHLINE_DEMO_OUT=artifacts/demo-conversational .venv/bin/python tools/demo/export_real.py
```
