# Expected Threat momentum

Implementation references:

- [socceraction xthreat.py](https://github.com/ML-KULeuven/socceraction/blob/master/socceraction/xthreat.py), `ExpectedThreat.rate(use_interpolation=False)` and `load_model`.
- [Karun Singh's pretrained grid](https://karun.in/blog/data/open_xt_12x8_v1.json), saved unchanged in `app/models/open_xt_12x8_v1.json`.
- [Original xT explanation](https://karun.in/blog/expected-threat.html).

Credit: Karun Singh for Expected Threat and the public grid; ML-KULeuven's
socceraction authors for the reference implementation. Our small inference
implementation follows the published method; it does not vendor library code.
No additional Python dependencies are required. The grid is a model surface,
not a copy of StatsBomb match events.

`app/xt.py` looks up start and end cells and returns end minus start threat.
StatsBomb's 120×80 top-left coordinates map to twelve columns and eight rows;
boundary coordinates map to the last cell. Both teams already face increasing x,
including after halftime. UI rotation must never affect inference. No interpolation
is applied. Backward movements can produce negative values; same-cell moves yield zero.

The direct event adapter includes completed passes (including open-play crosses)
and carries. It excludes pass outcomes indicating failure, explicit set-piece
restarts, shots, and take-ons. It does not reproduce full SPADL conversion or
infer additional dribbles between events. Invalid or missing movement coordinates
are excluded from action xT; the threat proxy tracks window-level coverage separately.

The public grid is fixed before replay; no replay events train or update it.
Its exact training corpus and calibration have not been independently verified.
Use this as a fan-facing attacking progression indicator, not a validated
historical prediction, VAEP, or proprietary StatsBomb OBV. It ignores defenders,
game state, failed movement costs and defensive contributions.

## Active match-momentum proxy

The active model in `app/peak_momentum.py` records each team's maximum
location-grid xT in each period-minute. It uses the destination of completed
open-play passes/carries and the starting location of shots. It does not add
signed movement deltas. A backward home movement therefore does not assign
threat to the away team.

Each peak is capped to [0, 0.1]. The current and previous three minute buckets
are averaged with weights `2 ** (-(period_seconds - bucket_start) / 60)`.
Unobserved future events never enter the current bucket. Quiet minutes have
zero threat; the window expires after four buckets. State resets each period,
and shootouts contribute no threat. Duplicate event IDs are ignored. Missing
eligible locations make that team's window incomplete until the affected bucket
expires; the chart leaves a gap instead of inventing a value.

The frontend samples one observed value per minute and draws a rounded filled
area around a central baseline: home above, away below. It uses a fixed symmetric
scale from the model cap, separates the halves and provides selectable goal
icons. Other shots remain on the shot map. Curve rounding is presentation only;
model values and AI context use the causal, unsmoothed calculation.

[FotMob's public chart](https://www.fotmob.com/en-GB/matches/chelsea-vs-arsenal/2rhhrp) inspired the visual treatment. We do not have its private
formula and do not claim output equivalence. The capped-minute-peak and recency
structure is informed by [Opta's public explanation](https://theanalyst.com/articles/what-is-match-momentum),
but our input is location xT, not its possession-value model. The four-minute
window, 60-second half-life and cap are explicit prototype choices. Values are
not scoring probabilities, win probabilities or independently calibrated pressure.
