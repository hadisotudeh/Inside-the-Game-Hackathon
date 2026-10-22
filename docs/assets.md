# Asset credits

## StatsBomb

Football data and supplied shot xG: [StatsBomb Open Data](https://github.com/hudl/open-data).
The app and overlay display the unmodified **hudl-statsbomb-logo-default** PNG
selected from [Hudl's official media kit](https://hudl.bynder.com/web/3995540F-A52E-4EB3-855B7726FCBC2983?viewType=grid&mediaId=27F9436E-E86A-4C0C-AF348B1C165B6D7B).
Asset ID: `27F9436E-E86A-4C0C-AF348B1C165B6D7B`. The media kit marks this asset
“External Use Approved.” The README requests source attribution and use of the
StatsBomb logo for published analysis and insights. The original 2258 × 344 PNG matching the supplied reference is stored
locally at `app/static/assets/statsbomb.png`; no expiring download URL is used by
the application.
Data remains fetched directly from the repository for selected matches.

## Club crests

The 20 Premier League club crests are downloaded from the thumbnail images on
their English Wikipedia club summaries. They identify the clubs in match replay;
each scoreboard crest links to its source article. Images are stored locally so
match selection does not depend on additional runtime Wikipedia requests.

[The source manifest](../app/static/assets/sources.json) records every club's
Wikipedia article, original image URL, and local asset path. Club crests and the
StatsBomb logo remain third-party marks and are not covered by this repository's
code license. Wikipedia availability does not establish a blanket redistribution
license; consult the corresponding image description and rights information for
the intended publication.

## Stadium backgrounds

`app/static/assets/stadiums.json` maps all supported clubs to their 2015/16 home
grounds, checked against the [season stadium table](https://en.wikipedia.org/wiki/2015%E2%80%9316_Premier_League#Stadiums_and_locations).
`app/static/stadium.js` requests freely licensed stadium page images using the
[PageImages API](https://www.mediawiki.org/wiki/API:Pageimages) and retrieves
author/license metadata via [Imageinfo](https://www.mediawiki.org/wiki/API:Imageinfo).
Photographer and license are displayed beneath the overlay, linked to the file
description. Photos are loaded remotely, not bundled; a dark gradient is applied
over the original image for readability. Photo date is not guaranteed to match
the replay season. A neutral background is used if lookup or loading fails.

## Demo titles and narration

The title cards use Microsoft and Premier League logos stored under
`tools/demo/assets/`. They identify the event organizers; the code license does
not grant trademark rights. Confirm organizer permission for submitted video use.
The final demo also shows historical club marks and a stadium photo with an
on-screen source credit. Recordings preserve the displayed attribution, but
permission for the required submission/promotional use remains an entrant check.

The final narration is synthetic speech modeled on Hadi Sotudeh’s own supplied
voice reference, approved by Hadi for use in the demo. It was generated locally
with [Kyutai Pocket TTS](https://github.com/kyutai-labs/pocket-tts), using
`pocket-tts` 4.0.1 and model `english_2026-09_2`. The model publisher lists
[CC BY 4.0](https://huggingface.co/kyutai/pocket-tts) for the weights; the
Pocket TTS software is MIT-licensed. Attribution: Kyutai, Pocket TTS. The
reference recording and derived voice state are private production inputs,
not repository assets. This narration is a demo-production choice, not an
Azure Speech integration or an application feature. No music or broadcast
match footage is included.
