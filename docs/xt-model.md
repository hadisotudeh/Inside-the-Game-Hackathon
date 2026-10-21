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
mark that half incomplete rather than fabricating values.

The public grid is fixed before replay; no replay events train or update it.
Its exact training corpus and calibration have not been independently verified.
Use this as a fan-facing attacking progression indicator, not a validated
historical prediction, VAEP, or proprietary StatsBomb OBV. It ignores defenders,
game state, failed movement costs and defensive contributions.

Momentum now shows individual action xT changes, with no accumulation or time decay.
For each event, the acting team receives action_xT and the other team receives zero.
The chart plots home minus away as one vertical mark per nonzero action. Positive
values use the home color; negative values use the away color. A backward movement
can favor the opponent. Non-rated events contribute zero; missing movement
coordinates make only that action incomplete. Duplicate events never count twice.
Shots remain separate markers sized by xG.

## Experimental peak-threat comparison

The app uses only per-action progression. The experimental model
is retained in `app/peak_momentum.py` as an inactive backup; it is neither computed
nor streamed during replay, and there is no calculation selector.

`app/peak_momentum.py` records the maximum destination-cell xT of completed
open-play passes/carries, or starting-cell xT of shots, per team per period-minute.
Each maximum is capped to [0, 0.1]. The current and previous three minute buckets
are averaged with weights `2 ** (-(period_seconds - bucket_start) / 60)`.
Quiet minutes contribute zero; the partial current minute contains only observed
events. State resets each period, and shootouts contribute no threat. Missing
locations are skipped. The chart connects event-time samples linearly.

This borrows the capped-minute-peak and recency-weighting structure described by
[Opta Analyst](https://theanalyst.com/articles/what-is-match-momentum), but uses
location xT rather than their proprietary next-10-seconds possession-value model.
The four-minute window and 60-second half-life are our choices, not published
Opta weights. Values must not be read as scoring probabilities.
