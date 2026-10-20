# Inside the Game

An early foundation for a personalized football intelligence experience for the
Microsoft / Premier League Inside the Game hackathon.

## Local setup

Requires Python 3.14 and Pipenv. Python 3.14 matches the development machine.
Run commands from the repository root:

```bash
PIPENV_VENV_IN_PROJECT=1 pipenv sync --dev
cp .env.example .env
pipenv run dev
```

Open http://127.0.0.1:8000/docs for the API documentation.
`GET /health` returns `{"status":"ok"}`. No cloud account or API key is needed.

Open **http://127.0.0.1:8000/** for **Touchline**, the live matchroom. Select a
StatsBomb Premier League match and start replay to see the event pitch, score/clock, shot map,
momentum timeline, and evidence-linked insights. All assets are served locally;
optional Google Fonts fall back to system fonts when offline. The browser frontend
uses plain JavaScript/SVG and needs no Node package manager or build step.

See the [demo guide](docs/demo.md) for the viewing modes and presentation sequence.

```bash
pipenv run test
pipenv run lint
pipenv run format --check
```

Commit both `Pipfile` and `Pipfile.lock`. Install reproducibly with `pipenv sync`;
use `pipenv install PACKAGE` or `pipenv install --dev PACKAGE` to add dependencies.
The lock file pins resolved versions and hashes. `.venv`, `.env`, and downloaded
data stay out of version control.

## Current scope

Match selection, historical event replay, and incremental momentum and shot-map
data are implemented. Optional Microsoft Foundry explanations and a labeled local
template mode are implemented. Foundry has not yet been verified against a real
deployment. The responsive viewing interface uses StatsBomb exclusively. Synthetic match
selection has been removed; the seeded generator remains an internal test utility.

## Optional match explanations

Explanations are opt-in per stream:

```bash
curl -N 'http://127.0.0.1:8000/matches/3754217/stream?speed=60&insights=true&audience=analyst'
```

Choose `audience=casual` (default) or `analyst`. In the default configuration,
`insight` SSE messages are deterministic English templates labeled
`provider=template` and `ai_generated=false`; they make no model calls.

To enable real inference, copy `.env.example` to `.env` and configure:

```dotenv
GAME_EXPLANATION_PROVIDER=foundry
GAME_FOUNDRY_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com
GAME_FOUNDRY_DEPLOYMENT=YOUR-DEPLOYMENT-NAME
GAME_FOUNDRY_API_KEY=YOUR-KEY
```

Use an Azure OpenAI deployment in Microsoft Foundry that supports chat completions
with strict JSON-schema structured outputs. The endpoint is the HTTPS resource
root (also supported: your Foundry resource's `https://RESOURCE.services.ai.azure.com`
root), not a project URL, `/models`, or `/openai/v1` URL. The provider calls
`/openai/v1/chat/completions` using the server-side API key. The deployment name
is your Azure deployment identifier. Restart the API after configuration changes.
No extra dependencies are needed: the integration uses the existing HTTPX client.

Run one **potentially billable** smoke request with fictional facts:

```bash
pipenv run python -m app.check_foundry
```

Exit code 0 and `provider=microsoft_foundry` indicate a real successful response.
A labeled fallback exits with code 1. No live Foundry verification has been run
as part of development so far; mocked HTTP tests are not evidence of Azure access.

Insights trigger on shots only. By default, each connection allows at most 12
requests with at least 30 wall-clock seconds between request starts and one
request in flight. Shots arriving while busy are skipped for explanations;
analytics still process every event. Faster replays therefore produce fewer
insights. These are per-connection limits, not a subscription-wide spending cap.
Requests time out after 10 seconds and are not retried. Settings are in `.env.example`.

Model input contains only the triggering event's analytics snapshot and team names,
not the full historical fixture. Output is schema-validated, and cited event IDs
must match the triggering shot. Model prose can still be inaccurate; this is not
a factual-proof system. Render text as plain text. Model failure, refusal,
truncation, invalid output, and timeout fall back to a clearly labeled template.

`insight` messages include `as_of_event_id`, evidence IDs, audience, provider,
`ai_generated`, and a sanitized `fallback_reason`. They can arrive after newer
events; anchor them to `as_of_event_id`, not the latest chart state. Streaming
continues during inference. Completion waits for the bounded pending request;
disconnecting cancels it locally (this does not guarantee Azure stops billing).
Set `GAME_EXPLANATION_PROVIDER=off` to disable explanations globally.

## Match replay and analytics

`GET /matches` fetches available Premier League 2015/2016 fixtures directly from
StatsBomb (competition 2, season 27), omitting final scores.

The app and public API use StatsBomb exclusively, with no source selector.
A network connection is required to fetch fixtures and events. Club crests are
served from local Wikipedia-sourced assets, and the official StatsBomb logo is
shown with linked attribution. Asset origins are recorded in
[the asset credits](docs/assets.md). Score updates use emitted goals/own goals only.

```bash
curl -N 'http://127.0.0.1:8000/matches/3754217/stream?speed=60'
```

The SSE endpoint emits `match`, `update`, then `complete` messages. Each
`update` includes the current event, momentum, a `shot_added` delta (null for
non-shot events), and cumulative shot/xG totals by team ID. A client builds its
shot map by appending each non-null `shot_added`; event IDs support deduplication.
Browser clients can use `EventSource` and close it on `complete` or `error` to
avoid automatic replay restarts. Reconnecting starts a fresh replay; resume is
not implemented. Each connection has independent state.

Replay defaults to real-time event spacing; `speed=60` compresses one match minute
to one second. Allowed speeds are 0.1–1000. Period breaks are skipped, timestamps
reset per period, and stoppage time is retained. Disconnecting stops the replay.
Data is downloaded into server memory before streaming and is not cached on disk.
This is simulated live historical data, not a live feed or synthetic dataset.

**Momentum:** computed xT for completed open-play passes/crosses and recorded
carries. Each movement receives end-cell minus start-cell value from Karun
Singh's public pretrained 12×8 grid, recommended by socceraction's `load_model`.
Each action adds its signed value to its team's exponentially decaying total.
Influence halves every 15 seconds of match time; there is no hard cutoff. Period
changes reset the totals and shootouts are excluded. The chart plots home minus
away at each event and traces exponential decay between events, without 30-second
bucketing. The vertical scale adapts to observed values. Football markers identify
shots at their event timestamps, sized by xG. Shots, failed passes and restarts do
not add xT. This measures attacking progression, not defensive value or win probability.

Payload: `metric=xt`, model identifier, `aggregation=exponential_decay_sum`,
`half_life_seconds=15`, current `action_value` (null for unvalued actions), home/away
smoothed totals, `net_difference`, `period_observations` and `missing_movements`
(number of teams with missing movement coordinates). Missing coordinates mark that
team and the comparison null (`status=incomplete`) until the next period reset;
otherwise status is `available`. `source_values_seen` counts computed movements.

See [xT model provenance and limitations](docs/xt-model.md). This is a lightweight
implementation of socceraction's non-interpolated inference rule, using a direct
StatsBomb adapter; socceraction itself is not installed (its published Python
constraint excludes this project's Python 3.14). No models are fitted on replayed
matches and no future match events are used for inference. The public grid's
training corpus is not verified here, so no claim of an independent historical
backtest or Premier League calibration is made.

**Shot map:** the API retains StatsBomb's 120 × 80 coordinates, where both teams
attack toward increasing x. The frontend uses opposing directions: home attacks
right in the first half and left in the second; away does the reverse. This is a
display convention, not a recovered stadium/camera orientation. Rotate leftward
actions by 180°: `(x, y) → (120 − x, 80 − y)`; shot height stays unchanged.
Apply the same transform to all freeze-frame players and the shot endpoint using
the shooting team's direction, including opponents and goalkeepers.

**Follow match** shows the current half and changes ends at halftime. The period
selector also supports either half and the whole match. Displayed shot/xG totals
follow that period selection; team filters affect markers only. Whole-match mode
retains each shot's period-specific position, so each team can have shots at both
ends. Replay score and momentum remain match-based. Direction labels identify the
current view, and shot snapshot captions identify their own period/direction.
Each marker includes player, event ID, match minute/second, period, outcome,
body part, type, and supplied StatsBomb xG (not an independently trained model).
A missing location remains null and cannot be plotted; the shot still counts.
Shootout shots are marked separately and excluded from momentum and match totals.
Only shots already emitted appear in the state. No final score is sent.

**Shot snapshots:** each shot delta also includes `freeze_frame` (an empty list
when unavailable) and the recorded shot `end_location`. Freeze-frame entries
contain recorded player coordinates, identity, position, a `teammate` flag relative
to the shooter, and a derived `goalkeeper` flag. These are shot-time snapshots,
not StatsBomb 360 or continuous tracking, and may not include every player.

The shot snapshot pitch follows newly emitted shots. Selecting a shot marker or
its commentary link pins that snapshot while replay continues; **Follow latest
shot** returns to automatic updates. Shooter rings and goalkeeper squares distinguish
roles; player names appear on hover or keyboard focus. If no frame is available,
the panel clears the previous positions and displays an unavailable message.
Freeze-frame coordinates are omitted from model prompts; narrative context remains
the measured shot/momentum summary.

Planned flow: event source → replay clock → incremental match state → grounded
explanations → personalized fan experience. The replay clock should support
speed control, period boundaries, cancellation, and independent viewer sessions.
Only events already emitted may enter match state or AI context; final scores
and future events must not leak into a replay.

## Data and hackathon requirements

See the [Microsoft integration and deployment plan](docs/microsoft-deployment.md)
for component-to-service mapping, current implementation status, and work needed
before Azure deployment. Development remains local; no Azure resources or paid
model calls are enabled. Planned deployment is not evidence of actual platform use.

See [the project brief](docs/project-brief.md) for the source policy, proposed
architecture, submission checklist, and feature ideas. Historical StatsBomb
replay alone does not satisfy the requirement to use synthetic data. The optional
Foundry adapter must be exercised against a real deployment before claiming
verified Microsoft AI usage in the submission.

The repository's existing LICENSE covers our code, not third-party datasets.
