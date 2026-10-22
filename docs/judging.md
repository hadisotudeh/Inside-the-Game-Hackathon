# Judge testing guide

Touchline is a Python web application for desktop browsers. The synthetic build
uses fictional teams and events generated locally; the historical case study in
the video is a separate mode. Both use the same analytics and AI workflow.

## Install and run the synthetic build

Requirements: Python 3.14, Pipenv, a modern desktop browser, and network access
for dependency installation. No account, login, dataset download, Chrome
automation, FFmpeg, or video-production tools are needed for ordinary testing.

```bash
git clone https://github.com/hadisotudeh/Inside-the-Game-Hackathon.git
cd Inside-the-Game-Hackathon
PIPENV_VENV_IN_PROJECT=1 pipenv sync --dev
cp .env.example .env
pipenv run demo
```

Keep an existing `.env` rather than overwriting it. Open
<http://127.0.0.1:8012/overlay>. Select Northbridge FC v Southbank United and
start replay at 60×. A full 90-minute replay takes about 90 seconds.
The visible source badge identifies synthetic replay and seed 42.

1. Watch the clock, player labels, score, events, shot map and statistics update.
2. Select a shot marker to inspect the shooter, outcome and illustrative xG.
3. Inspect momentum and switch teams in the passing network. Only completed
   passes create links. Shot snapshots are absent because this generator does
   not manufacture player freeze frames.
4. With Gemini configured below, ask “Who has created the better chances so far?”
   The answer reports its snapshot time; later replay events are not added to it.
5. Stop/reset the replay and repeat. The same seed produces the same events.

## Test the real AI workflow

Set `GAME_GEMINI_API_KEY` and an accessible `GAME_GEMINI_MODEL` in the server's
`.env`, then restart. Use a key you are authorized to use; do not put it in the
browser or public repository. The final historical recording used a real
Gemini response, not a fixture or canned answer.

Without a key, replay and analytics work and chat returns an explicit 503.
Quota/provider failures remain visible and do not stop replay. Mocked provider
tests verify error handling but are not evidence of live Foundry inference.
Casual mode is exposed in the overlay; the API also accepts `mode: "analyst"`.

The release owner must arrange authorized model access for judging if judges
are to exercise AI without supplying their own key. No public app or private
judge credentials have been provisioned by this repository preparation.

## Historical video case study

Stop the synthetic server if desired, then run `pipenv run dev` and open
<http://127.0.0.1:8000/overlay>. Choose Chelsea–Arsenal, September 19, 2015.
This mode fetches StatsBomb historical events over the network. The recording
adds 60× playback and editorial camera moves; the ordinary overlay offers 1×/2×.
Historical events are not synthetic. See [credits](assets.md) for data and assets.

## Automated verification

```bash
pipenv verify
pipenv run lint
pipenv run format --check
pipenv run test
```

Tests cover replay ordering, incremental calculations, passing networks, synthetic
consistency, source isolation, evidence collection, and provider handling. They
do not make billable cloud calls or require production credentials.

## Current boundaries

The synthetic generator has structurally checked football events, not independently
validated match realism. Its xG is illustrative. There is no continuous tracking,
video inference, licensed live feed, production broadcast synchronization, global
model spending cap, or tested Azure deployment. Foundry is an optional adapter
awaiting real-service verification. The workflow has deterministic evidence
collection and narration stages, rather than autonomous multi-agent negotiation.

The prototype accepts client-provided snapshots. A shared public deployment needs
authoritative match sessions and request controls before exposing model credentials.
