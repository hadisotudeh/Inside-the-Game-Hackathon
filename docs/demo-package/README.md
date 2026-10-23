# Touchline — Azure demo

[Open the live app](https://touchline-inside-the-game.azurewebsites.net) · [Download the updated demo](../../artifacts/demo/touchline-demo.mp4) · [Transcript](narration.txt) · [Captions](captions.srt)

**114.67 seconds · 1920×1080 · 30 fps · H.264/AAC · English**

The demo defines event data as individual timed actions with players and locations, and explains how streaming a historical match one event at a time simulates a live scenario.

The opening slide transitions directly to the public Azure URL screen, with no intermediate app glimpse. The demo then navigates to the actual
hosted application, replays historical Chelsea–Arsenal events, explores charts,
and demonstrates both dropdown modes: a real question and the default automatic
AI interpretation timeline through Azure-hosted GPT-4.1 mini in Microsoft Foundry.
Microsoft Agent Framework runs all three evidence tools. The concise voiceover explains the three evidence tools, answer-format and event-reference checks, automatic notes, and shared evidence across both modes. The voiceover explains narration and chat separately while their actual outputs remain visible, with no side text panel. The bounded, fixed-tool design is stated explicitly. The recording uses the built-in 15× speed and zooms in on momentum, whose axis expands with elapsed play. The app footer and closing slide credit [Hadi Sotudeh](https://www.linkedin.com/in/hadisotudeh).
The app credit is clickable; the final video slide shows a LinkedIn logo beside the developer credit, without displaying the profile URL. The opening introduces match statistics and AI for football fans and commentators. The voiceover closes with “Developed by Hadi Sotudeh,” then “For more, follow me on LinkedIn. Bye,” followed by a silent closing pause.
A 28-second architecture walkthrough explains historical events, FastAPI replay and analytics, streaming browser charts, the three Agent Framework tools, Azure inference, and server-side response checks. Diagram highlights follow each spoken step before the closing slide.
The closing slide says
that hosting and Azure AI are already live and repeats the public address.
No match data or model answer is fabricated for the recording. The URL launcher,
chapter labels, camera movements and closing slide are editorial presentation.
The underlying data remains historical StatsBomb events, not a live match feed.

Narration uses Hadi Sotudeh's authorized private voice reference and the same
saved voice state as the earlier demo, generated locally with Kyutai Pocket TTS.
All nine chapters use pitch-preserving playback at 0.88× the original voice pace. Ten extra seconds let viewers read the charts, AI outputs, and architecture. Complete takes preserve breathing and word endings; fades are limited to non-speech edges. One fixed volume adjustment across the whole narration avoids abrupt changes between sections.
There is no music or broadcast footage. Captions are sentence-timed estimates.
The private reference, voice state, authentication and intermediate media stay
outside Git. The previous release is preserved locally under `.demo-production/production/previous-release`.

## Evidence

- [Real hosted-site response and browser report](recording-report.json)
- [Voice provenance and natural chapter durations](narration-report.json)
- [Media metadata](media-report.json)
- [Timeline and script](timeline.json)

See [production instructions](../../tools/demo/README.md),
[asset credits](../../docs/assets.md), and [judge instructions](../../docs/judging.md).

## Publication

[Watch the latest demo on YouTube](https://youtu.be/Q1jKv-HsTxo). The same final MP4 is available in the repository.
