# Touchline demo package

Final video: `artifacts/demo/touchline-demo.mp4` (1:58, 1920×1080, H.264/AAC).
English synthetic voiceover, visible captions, selectable English subtitle track,
original opening/closing graphics, browser footage and close-ups. No music or
match footage. Transcript and captions are in `artifacts/demo/`.

## What was recorded

This is the actual `/overlay` UI with the existing SSE replay, analytics and
Agent Framework/Gemini chat. `server.py` selects the existing fictional generator
(seed 42) instead of historical data. Its small adapter adds possession IDs and
pass recipients for the possession and network displays. All 693 events pass
through the ordinary analytics engine. No answers or statistics are mocked.

The separate demo build replaces historical branding, removes stadium imagery,
labels synthetic replay and heuristic xG, and offers 60× replay. Camera moves,
highlights and titles are editorial additions. Editorial CSS also exposes the
existing selected-shot details, which the normal overlay stylesheet hides.
The default application and its historical source are unchanged.

Two takes of the same seeded replay are edited together (`edit.json`). The first
contains a real HTTP 200 Gemini response, with Microsoft Agent Framework and all
three evidence tools reported by the backend. Its second question receives a
real HTTP 429 quota error, shown during the reliability section. The clearer
selected-shot segment comes from the second take. That take's AI request also
received HTTP 429; it is not substituted for the successful AI segment.
The editorial quote at 1:03 repeats the successful response verbatim and is
labeled with its original snapshot time, 48:56. It is not another AI request.

Narration uses the synthetic `en-GB-RyanNeural` voice through edge-tts. Narration
is a video production asset, not a feature claimed for the app. Azure deployment
and production broadcast synchronization are explicitly described as next steps.
The two deterministic workflow stages are not presented as independently
reasoning autonomous agents.

## Rules checked, October 21, 2026

The supplied [event page](https://innovationstudio.microsoft.com/hackathons/insidethegamedeveloperhackathon)
redirected to Microsoft sign-in. No private event-page content was accessible.
Rules were checked against Microsoft's [official rules](https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md).

The video stays below two minutes, shows functioning software, uses English,
and demonstrates synthetic events with explainable on-screen intelligence.
Before submission, confirm registration and entrant eligibility, data/asset
permissions, category fit, a public GitHub repository, a public video URL on an
accepted host, and a judge-accessible build through the end of judging.
A video alone does not establish eligibility or guarantee a winning entry.

Product work remains: the synthetic generator is deliberately simple, with
completed passes/carries/shots and heuristic xG. Its football realism has not
been evaluated; failed passes, defensive events and richer player behavior need
work. Audience personalization in the overlay is through questions and team
selection; the visible chat currently uses casual mode. The existing API also
supports analyst mode. Do not claim tested Azure hosting, Foundry inference,
production feed synchronization, calibrated synthetic xG, or full category
compliance on the strength of this recording.

## Reproduce and edit

Run from the repository root. Normal application dependencies use the existing
Pipenv environment. Production tooling also requires FFmpeg, Chrome/Chromium,
Playwright and edge-tts. For this build, the latter two were installed into
`/tmp/touchline-video-tools`, without changing application dependencies.

```bash
.venv/bin/python -m tools.demo.server
# In a second terminal (network access is needed for voice and real Gemini):
PYTHONPATH=/tmp/touchline-video-tools .venv/bin/python tools/demo/voice.py
PYTHONPATH=/tmp/touchline-video-tools .venv/bin/python tools/demo/record.py
.venv/bin/python tools/demo/export.py --latest
```

For the exact supplied edit, keep both original raw takes and run `export.py`
without `--latest`. `edit.json` lists their paths. Edit `story.json` for narration
and timing, `editorial.css` for recording presentation, and `export.py` for final
caption/quote styling. Remove the corresponding cached `voice-N.mp3` before
regenerating a changed narration chapter. Caption timings are estimated within
chapters and can be refined in `captions.srt`.

Raw recordings and audio are intentionally ignored by Git; the MP4 remains on
disk for review and upload. The tools do not publish or submit anything.

## Validation

- Final media metadata and full decode checked: 118 seconds, H.264 video,
  1920×1080, 30 fps, AAC audio, English mov_text subtitles.
- No browser JavaScript errors in either take. Successful first-take response
  reported `Microsoft Agent Framework` and `get_match_stats`,
  `get_recent_events`, `get_player_summary`; real quota errors were explicit.
- Synthetic source determinism, unique event IDs, analytics processing of all
  693 events, and nonempty passing-network links verified.
- Ruff passes for the demo tools.
- Existing app suite: 49 passed, 1 failed. The failure is an existing assertion
  in `tests/test_synthetic.py::test_viewing_routes_use_statsbomb_only` expecting
  `overlay-score` in the current overlay HTML. Neither that test nor the normal
  overlay HTML was modified by this work.

## White opening slide

Both recording scripts use `title_card.py` and the official logos in `assets/`.
The opening uses a white background, DejaVu Sans, a 124 px headline, and larger
supporting text. Render a standalone preview with:

```bash
PYTHONPATH=/tmp/touchline-video-tools .venv/bin/python tools/demo/preview_title.py
```

Preview: `artifacts/demo-real/opening-slide.png` (1920×1080).
The existing historical take with the revised opening is exported separately as
`artifacts/demo-real/touchline-demo-updated.mp4`; its original audio and subtitle
tracks are preserved. The original recording remains available.
