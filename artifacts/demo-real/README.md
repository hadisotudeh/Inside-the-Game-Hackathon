# Revised Touchline demo: historical Premier League case study

Video: **touchline-demo-real-match.mp4** — 1:58, 1920×1080, H.264/AAC,
English voiceover, visible captions and a selectable English subtitle track.

Recorded directly from **http://127.0.0.1:8000/overlay**. The selected fixture is
Chelsea–Arsenal, September 19, 2015, using the app's StatsBomb Open Data source.
The replay runs at 60×. No synthetic replacement source, fake event payloads,
mocked model responses, or broadcast match footage is used in this revision.

The narration explains:

- Touchline's intended use alongside live TV and streaming footage.
- Why an event-data pitch replaces broadcast footage in this demonstration.
- Event data: timestamped records of actions, players, locations and outcomes.
- A proposed live deployment receiving events through a licensed provider's API.
- This demonstration's historical, publicly available Premier League case study.
- Sequential event streaming, updating the pitch and statistics as events arrive.
- Shot quality, momentum, passing networks and questions about the match so far.

In this take, the real `/chat` request returned HTTP 429 because Gemini's free-tier
quota was exhausted. The video explicitly narrates that limitation while the
replay and analytics continue. An editorial card labels the real HTTP 429 response. No answer from the
earlier synthetic match was inserted. There were no browser JavaScript errors. Clock samples progress from
00:00 through 95:35; details are in `recording-report.json`.

The live API feed and synchronization with broadcast video are intended deployment
features; this recording demonstrates the existing historical replay, not a
verified live Premier League feed or production television integration.

## Voice and edit

The new voice is `en-GB-SoniaNeural`, generated at -2% speaking rate. There is no
post-generation time stretching or speech acceleration. Natural sentence timing
and pauses determine the camera changes. Captions use the speech service's
sentence timestamps rather than estimated word counts. The closing card holds
briefly to bring the final runtime to 1:58. The narration remains synthetic;
it is not represented as a human recording.

The recording uses presentation CSS, camera zooms and editorial titles. It also
exposes the app's existing selected-shot detail panel, which the standard overlay
stylesheet hides. Match data, analytics, replay logic and AI endpoints are
unchanged. The source attribution remains visible. No footage rights or blanket
data permissions are asserted merely because the data is publicly accessible.

## Submission context

This revision follows the requested historical-case-study positioning. Historical
event data alone does **not** fulfill the hackathon's separate synthetic-data
requirement. Keep the synthetic demonstration/build available and address that
requirement in the final project. See Microsoft's [official rules](https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md).
The event page supplied earlier required Microsoft sign-in.

The video is saved locally. Nothing has been uploaded, published or submitted.

## Reproduce

With the ordinary app running on port 8000, from the repository root:

```bash
PYTHONPATH=/tmp/touchline-video-tools .venv/bin/python tools/demo/voice_real.py
PYTHONPATH=/tmp/touchline-video-tools .venv/bin/python tools/demo/record_real.py
.venv/bin/python tools/demo/export_real.py
```

The temporary tooling directory contains Playwright and edge-tts. FFmpeg and
Chrome are also needed. `tools/demo/story-real.json` is the editable narration;
`timeline.json` records the resulting timings. `timeline-recorded.json` locks
the chapter positions to this recorded take; remove that lock file before
planning an entirely new edit with different chapter lengths. For changed text, remove only the
corresponding cached `voice-N.mp3` and `voice-N.json` before regenerating.
`recording-report.json` captures the source URL, actual AI request outcomes,
JavaScript errors and replay-clock samples. `media-report.json` captures the
final video/audio/subtitle codecs and runtime.
