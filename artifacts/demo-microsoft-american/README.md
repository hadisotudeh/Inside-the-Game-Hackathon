# Touchline — Microsoft integration demo

Natural-paced American male narration: en-US-GuyNeural, rate -2%.
The narration uses a synthetic voice, with no post-generation speech speed-up.

Script: tools/demo/story-microsoft.json, based on README.md and
docs/microsoft-deployment.md. The final slide identifies:

- Implemented: Microsoft Agent Framework and three evidence tools, with Gemini inference.
- Adapter implemented, live verification pending: Microsoft Foundry explanations.
- Proposed: Azure Container Apps, Web PubSub, Application Insights and Key Vault.

The demo preserves the white opening slide, event branding and organizer logos,
and “Ask the match via AI” with AI in bold.
A real Gemini preflight request returned HTTP 429. The recording makes another
real request and records its status in recording-report.json. No answer is invented.

Reproduce:

```bash
TOUCHLINE_DEMO_OUT=artifacts/demo-microsoft-american TOUCHLINE_DEMO_STORY=tools/demo/story-microsoft.json PYTHONPATH=/tmp/touchline-video-tools .venv/bin/python tools/demo/voice_real.py
TOUCHLINE_DEMO_OUT=artifacts/demo-microsoft-american TOUCHLINE_DEMO_MICROSOFT=1 PYTHONPATH=/tmp/touchline-video-tools .venv/bin/python tools/demo/record_real.py
TOUCHLINE_DEMO_OUT=artifacts/demo-microsoft-american .venv/bin/python tools/demo/export_real.py
```
