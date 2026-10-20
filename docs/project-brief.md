# Project brief

## Product direction

Let a viewer select a match and consume timestamped events as though live,
then add explanations and personalized experiences beyond a score timeline.
Use one normalized event contract for both synthetic events and optional
historical development replays. Preserve source type and provenance explicitly.

## Source policy

[Official hackathon rules](https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md),
sections 4.1 and 4.7, require synthetic, football-realistic events. Replaying
historical data or changing its timestamps does not make it synthetic.

The proposed historical source is [Hudl / StatsBomb Open Data](https://github.com/hudl/open-data).
Premier League 2015/2016 is competition `2`, season `27`:

- `data/competitions.json`: competition/season catalog.
- `data/matches/2/27.json`: available matches; do not assume complete season coverage.
- `data/events/{match_id}.json`: match events.
- `data/lineups/{match_id}.json`: lineups.

The supplied catalog record has no available 360 data. Event coordinates are
not continuous tracking data; do not claim player speed or distance without
appropriate observations.

StatsBomb's README requires source attribution and its logo for published,
shared, or distributed analysis/insights. Its separate
[data license](https://github.com/hudl/open-data/blob/master/LICENSE.pdf) must be
reviewed before integrating or redistributing data; open access is not blanket
permission for every use. Sections 1.2.1, 1.2.2, and 7 restrict redistribution,
commercial exploitation, and modification/transfer of the data. Obtain appropriate
permission before exposing historical raw events through a shared replay app.
No third-party data or logos are bundled here.
Use independently generated fictional matches for the submission by default;
document generation seeds, constraints, and any source influence. Verify rights
before using historical data to train or calibrate a generator.

## Implementation status and next steps

1. Match selection and per-session SSE replay are implemented for StatsBomb historical
   replay with explicit provenance and period clocks. Synthetic selection has
   been removed from the public interface and API.
2. An internal fictional 90-minute generator produces reproducible test events.
   Its distance-based xG is illustrative; evaluate realism before submission.
3. Incremental momentum, shot maps, and score updates feed the browser matchroom.
   Shot selection exposes evidence; a transparent same-browser overlay is available.
4. Casual/analyst explanations use either clearly labeled templates or the optional
   Foundry adapter. Live Foundry access and explanation quality still need verification.
5. Azure hosting remains planned. See [deployment status](microsoft-deployment.md)
   and [the demo guide](demo.md) for boundaries and submission work remaining.

Keep the initial system small. Add specialized agents only when distinct roles
and handoffs improve the outcome; choosing the multi-agent category is optional.

## Fan engagement ideas to evaluate

These are product hypotheses, not verified claims about competitor feature gaps:

- **Why now?** Explain a change in pressure or attacking pattern using recent
  event evidence and a simple pitch visualization.
- **Follow my player:** Build a rolling story around a chosen player's actions,
  with separate casual and analyst explanations.
- **Ask the match:** Answer questions using only events seen so far, showing
  supporting moments and acknowledging what event data cannot reveal.

## Submission checklist

- New project created during the permitted period and relevant category selected.
- Synthetic football-realistic data, explainable insights, on-screen output,
  and meaningful personalization.
- Actual Microsoft/Azure technology integration explained in the pitch.
- Public GitHub repository, reproducible instructions, and working demo/test build.
- Public demonstration video under two minutes and English submission materials.
- Judge access through the end of judging, November 10, 2026 Pacific Time.
- Registration: October 20, 2026 at noon Pacific Time.
- Submission: October 27, 2026 at 23:59 Pacific Time.

Judging weights: implementation, agentic innovation, impact, UX/presentation,
and category adherence, each 20%. Recheck official rules before submitting.
