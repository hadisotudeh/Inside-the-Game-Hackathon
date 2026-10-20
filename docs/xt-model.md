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

For each team the smoother follows S(t) = S(previous) × 2^(−elapsed/15) + action_xT.
Elapsed time is match time, independent of replay speed. There is no hard window
cutoff, future-event lookahead, or normalization by action count. Period changes
reset the state; duplicate events never add value twice. Missing movement coordinates
mark the affected team's state incomplete until the next period reset.

The UI plots home minus away at every event and traces exponential decay between
events, without time buckets. Shots are football markers sized by xG and can be
selected for inspection. This smoothing and visualization are app choices, not a
socceraction momentum model.
