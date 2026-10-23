# Touchline demo

[Watch the final MP4](../artifacts/demo/touchline-demo.mp4) · [Open the live app](https://touchline-inside-the-game.azurewebsites.net) · [Transcript and verification](demo-package/README.md)

The demo opens the public Azure address and replays historical Chelsea–Arsenal
StatsBomb events. It shows shot inspection, the dynamic momentum time axis,
passing networks, and both AI modes at the app’s built-in 15× replay speed. The momentum section uses a close-up; narration and chat are explained separately without a side text panel. The narration uses Hadi Sotudeh's authorized
voice reference with a pitch-preserving slower pace, smoothed joins, reading holds, and captions.

## Agent workflow shown in the demo

The default **AI interpretation timeline** requests timestamped interpretations
as the replay develops. **Ask the match** lets viewers request an explanation
with a question. Switching preserves notes and the conversation.

Both modes use Microsoft Agent Framework to run `get_match_stats`,
`get_recent_events`, and `get_player_summary` against the current match snapshot.
Azure-hosted GPT-4.1 mini generates a structured explanation; the app checks its
response structure and event references. The voiceover explains these steps while the video shows actual narration and chat output. These checks establish
structure and valid references, not a guarantee that every interpretation is correct.

This is a bounded workflow with fixed evidence tools and limits on automatic
interpretations. The recording does not claim autonomous tool selection, a live
licensed event feed, or broadcast synchronization. Those distinctions matter
when describing the project to judges.

## Try it yourself

Open the live app, choose a fixture and press **Start replay**. Leave the default
interpretation timeline selected to see automatic notes after the opening match
minute, then choose **Ask the match** and submit a question.

For local setup and server-side model credentials, see the [README](../README.md#enable-local-ai-narration-and-chat).
For the separate seeded synthetic judge build, follow the [judge guide](judging.md).

[Watch the latest demo on YouTube](https://youtu.be/Q1jKv-HsTxo). See the
[submission checklist](submission.md) and [production instructions](../tools/demo/README.md).
