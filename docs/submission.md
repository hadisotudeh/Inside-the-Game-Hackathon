# Submission package

Repository: <https://github.com/hadisotudeh/Inside-the-Game-Hackathon>

**Status: repository prepared locally; external submission steps remain.**
The GitHub API confirmed the repository is public on October 22, 2026;
the changes in this package still need to be pushed.
Live application: <https://touchline-inside-the-game.azurewebsites.net>.
The latest demo is published on [YouTube](https://youtu.be/Q1jKv-HsTxo); use this URL in the project form.

## Description for the project form

**Touchline**

Your AI football companion: live stats, match stories, and answers for fans and commentators ⚽💻

Touchline helps football fans and commentators follow a match through interactive statistics and AI explanations. Shot maps, passing networks, and an attacking-threat chart update as events arrive. The default **AI interpretation timeline** adds automatic match notes; **Ask the match** answers questions using the same evidence.

Built with **Python/FastAPI**, **Microsoft Agent Framework**, and **Azure-hosted GPT-4.1 mini through Microsoft Foundry**, Touchline gathers match statistics, recent events, and player summaries through three tools. The server checks the response format and cited event references before displaying explanations.

**Already live on Azure App Service**, the app simulates live play by streaming a historical Chelsea–Arsenal match from [Hudl/StatsBomb Open Data](https://github.com/hudl/open-data) one event at a time. A separate synthetic build generates seeded fictional matches. Production live feeds and broadcast synchronization remain future work.

Developed by **[Hadi Sotudeh](https://www.linkedin.com/in/hadisotudeh)** for the **Microsoft × Premier League Inside the Game Developer Hackathon**.

[Watch the demo](https://youtu.be/Q1jKv-HsTxo) · [Try Touchline](https://touchline-inside-the-game.azurewebsites.net) · [GitHub and setup](https://github.com/hadisotudeh/Inside-the-Game-Hackathon)

## Evidence supplied

| Item | Location or status |
| --- | --- |
| Working code and dependency lock | Root application, Pipfile and Pipfile.lock |
| Judge setup and synthetic build | [Testing guide](judging.md); `pipenv run demo` |
| Final English video | [Approved demo](../artifacts/demo/touchline-demo.mp4), 114.67 seconds, 1080p; owner-reference synthetic narration |
| Video transcript and captions | [Demo package](demo-package/README.md) |
| Live integration evidence | Hosted app and updated recording: Foundry HTTP 200, Agent Framework, three evidence tools |
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
- [x] Publish the updated Azure demo on [YouTube](https://youtu.be/Q1jKv-HsTxo).
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

The hosted demo uses Agent Framework orchestration and Azure-hosted GPT-4.1 mini through Microsoft Foundry. Its evidence and narration stages follow a fixed workflow. The optional shot-explanation adapter still needs a live deployment check. Select the category that fits this implementation.

## Rights review before upload

The historical video includes club marks, Microsoft/Premier League logos,
StatsBomb attribution, and a remotely sourced stadium image. Provenance is not
permission. Confirm the necessary rights for submission and promotion; the MIT
code license does not license those assets. The final narration uses the owner’s supplied voice reference with permission;
Pocket TTS attribution is recorded in the asset credits. If permission is unavailable, use a cleared synthetic recording instead.
