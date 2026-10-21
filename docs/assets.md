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
