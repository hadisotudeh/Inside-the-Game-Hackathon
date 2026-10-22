# Touchline demo

The final recording is documented in [the demo package](../artifacts/demo/README.md).
For synthetic judging, follow [the judge guide](judging.md) and run `pipenv run demo`.
The instructions below describe the separate historical application.

## Run locally

```bash
pipenv sync --dev
pipenv run dev
```

Open http://127.0.0.1:8000/. Choose a StatsBomb Premier League 2015/2016 fixture. A network connection is
required; template explanations do not need cloud credentials. Start replay at
30× for roughly three minutes or 60× for roughly 90 seconds, plus stoppage time.
Speed or audience changes start a fresh replay rather
than pretending to resume from a known point. Stop and reset controls are explicit.

## What the viewer sees

- Page order: match score, xT momentum, shot map, then event-location pitch.
  Match notes sit alongside on desktop and follow the pitches on mobile.
- Match header: running score/clock and the latest event. The event-location pitch
  is visible below the shot map; it shows recorded positions, not continuous tracking.
- Shot map: marker size represents StatsBomb xG; filled markers are
  goals. Filter by team and click or keyboard-select a marker for details.
  Teams attack opposing goals, with ends switching at halftime. **Follow match**
  shows the current half; choose either half or **Whole match** explicitly. Shot/xG
  totals follow the selected period. The display convention starts home attacking
  right; normalized source data does not establish the original stadium orientation.
- Shot snapshot: show recorded players at the shot moment where a freeze frame
  exists. The shooter has a ring; goalkeepers use squares. Selecting an earlier
  shot pins its snapshot; **Follow latest shot** restores automatic updates.
  Hover or focus players for names. Missing snapshots are labeled and cleared.
- Momentum: smoothed per-action signed xT from completed open-play passes and carries,
  using the public pretrained grid recommended by socceraction. Explain the
  15-second smoothing half-life, home-minus-away bars, and that defensive actions are excluded.
- Match notes: **Overview** for concise commentary or **Detailed** for xG and
  measured context. Shot links expose the evidence. Labels distinguish templates,
  fallback templates, and Foundry.

Insights are event-driven and may be delayed relative to a shot. Default inference
cooldown is 30 real seconds, including during accelerated replays. For a local
template-only presentation with more frequent cards, set
`GAME_EXPLANATION_INTERVAL_SECONDS=5` and restart the server. This also changes
request cadence if Foundry mode is later enabled; keep the per-session budget.

## Overlay preview

Open the header's Overlay view link in the same browser while the matchroom is
open. `/overlay` has a transparent background, compact scoreboard, and the latest
insight. It receives updates through BroadcastChannel from the main tab, including
current state when it opens mid-replay. Use one active matchroom at a time.

This demonstrates the presentation format. It is not a broadcast system
integration: an OBS browser source or another device/browser cannot subscribe to
the in-browser channel. Production overlays need a server-backed shared session,
synchronization to the video clock, and suitable feed/footage rights.

## Suggested presentation, under two minutes

1. Explain the problem: a score tells you what happened; viewers need context.
2. Start a selected StatsBomb match at 60×. Show shot markers appearing only as
   events arrive. Explain how completed movements add or reduce xT in the smoothed curve.
3. Select a shot to expose its outcome, player, and xG. Show an insight and its
   supporting-shot link. Explain xG is supplied by StatsBomb.
4. Show casual versus analyst output; audience changes explicitly restart replay.
5. Show the overlay preview to connect the interface to a streaming/broadcast use.
6. If real Foundry is configured and verified, show its generated output and
   label. Otherwise identify templates honestly; do not claim tested AI inference.

## Submission work still open

The final historical demo records a successful Gemini answer. The synthetic test
build has separate judge instructions. Real Foundry verification, explanation
evaluation, and the external release steps in [the submission checklist](submission.md)
remain open. No winning
outcome or eligibility is guaranteed by the interface or architecture.
