# Touchline — final demo

[Watch on YouTube](https://youtu.be/o-lBHqRdArY) · [Download the approved demo](touchline-demo.mp4) · [Transcript](narration.txt) · [Captions](captions.srt)

**86.98 seconds · 1920×1080 · 30 fps · H.264/AAC · English**

**YouTube URL:** <https://youtu.be/o-lBHqRdArY>. Use this link in the hackathon
submission form. The GitHub download is also supplied for review.

This is the single approved demo. Previous voice versions have been removed.
The video shows the actual historical Chelsea–Arsenal overlay recorded October
22, 2026. A live Gemini question returned HTTP 200 through Microsoft Agent
Framework and all three evidence tools, comparing chances at the 37:10 snapshot.
No browser JavaScript errors were reported.

The narration is synthetic speech modeled on Hadi Sotudeh’s own supplied voice
reference, generated locally with Kyutai Pocket TTS and approved by Hadi. All
eight chapters fit their recorded slots without speeding up the speech. The
picture stream is unchanged from the recorded edit, including the opening,
closing slide, and burned-in captions. Sentence-level caption timing may differ
slightly from the generated narration. There is no music or broadcast footage.
Foundry verification and Azure deployment are explicitly pending/proposed.

## Verification and evidence

- [Recorded Gemini response and browser report](recording-report.json)
- [Narration provenance, chapter timing and picture-stream verification](narration-report.json)
- [Media metadata](media-report.json)
- [Timeline and script](timeline.json)

The final MP4 is included in Git and passed a full media decode. Local reference
audio, derived voice state, intermediate audio, raw browser take and screenshots
are excluded. See [production instructions](../../tools/demo/README.md) for
reproduction and [asset credits](../../docs/assets.md) for attribution.

This historical case study is distinct from the runnable synthetic judge build.
Follow [judge testing instructions](../../docs/judging.md) and the
[submission checklist](../../docs/submission.md) for the remaining release steps.
