# Submission package

Repository: <https://github.com/hadisotudeh/Inside-the-Game-Hackathon>

**Status: repository prepared locally; external submission steps remain.**
The GitHub API confirmed the repository is public on October 22, 2026;
the changes in this package still need to be pushed.
YouTube video URL: <https://youtu.be/o-lBHqRdArY>. Add this link to the hackathon
project form.

## Pitch for the project form

Touchline helps football fans understand the story behind the score. It turns
timestamped events into an interactive broadcast-style companion: chance quality,
attacking momentum, passing connections and questions about the match so far.

Microsoft Agent Framework coordinates three evidence tools and a narrator stage.
Gemini explains the captured match state, with schema checks, citation validation
and a visible snapshot time. A separate synthetic build creates seeded fictional
matches locally; the recorded case study demonstrates the same interface on
historical Chelsea–Arsenal events. Questions, team selection and shot exploration
let viewers investigate what interests them.

The application is a working local prototype. Agent Framework and real Gemini
inference are demonstrated. A Microsoft Foundry explanation adapter is implemented
but awaits live verification. Azure Container Apps, Web PubSub, Application Insights
and Key Vault are proposed deployment integrations. Production live feeds, broadcast
synchronization and independent evaluation of synthetic realism remain future work.

## Evidence supplied

| Item | Location or status |
| --- | --- |
| Working code and dependency lock | Root application, Pipfile and Pipfile.lock |
| Judge setup and synthetic build | [Testing guide](judging.md); `pipenv run demo` |
| Final English video | [Approved demo](../artifacts/demo/touchline-demo.mp4), 86.98 seconds, 1080p; owner-reference synthetic narration |
| Video transcript and captions | [Demo package](../artifacts/demo/README.md) |
| Live integration evidence | Final recording: Gemini HTTP 200, Agent Framework, three evidence tools |
| Architecture and service status | [README](../README.md), [Microsoft plan](microsoft-deployment.md) |
| Source and asset provenance | [Credits](assets.md), [xT model](xt-model.md), [MIT code license](../LICENSE) |

## Release checklist

The [official rules](https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md)
were checked October 22, 2026; they control eligibility and acceptance.

- [ ] Confirm timely registration, residency/age eligibility, team representation,
  original work, project dates, and required third-party permissions (sections 3–4).
- [ ] Review synthetic football realism and category fit (4.1–4.3, 4.7).
  Historical footage alone is not the synthetic-data demonstration.
- [ ] Push the reviewed changes and verify the repository is public without login.
- [ ] Confirm GitHub Actions is green for the exact submitted commit.
- [x] Upload the final video to an accepted host: [YouTube demo](https://youtu.be/o-lBHqRdArY).
- [ ] Confirm the video is viewable without login and add its URL to the project
  form. The video must stay under two minutes (4.4).
- [ ] Provide the test-build link and [testing instructions](judging.md), with
  authorized AI access, free and unrestricted through judging (4.8).
- [ ] Complete the English project form and submit before October 27, 2026,
  11:59 pm Pacific Time (October 28, 10:29 am Tehran).

Registration closed October 20 at noon Pacific. Judging ends November 10 at
11:59 pm Pacific. Section 3 excludes residents of listed locations, including
Iran; a timezone alone does not establish residency. Confirm eligibility directly
with the organizer if uncertain.

The strongest demonstrated Microsoft component is Agent Framework orchestration.
Do not claim verified Foundry use or Azure deployment, or describe the two workflow
stages as independently reasoning agents. Category selection remains an entrant
decision against the actual implementation.

## Rights review before upload

The historical video includes club marks, Microsoft/Premier League logos,
StatsBomb attribution, and a remotely sourced stadium image. Provenance is not
permission. Confirm the necessary rights for submission and promotion; the MIT
code license does not license those assets. The final narration uses the owner’s supplied voice reference with permission;
Pocket TTS attribution is recorded in the asset credits. If permission is unavailable, use a cleared synthetic recording instead.
