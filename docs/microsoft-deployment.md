# Microsoft integration and deployment plan

## Status

The application runs locally with Pipenv. **Microsoft Agent Framework is integrated
and has executed a real Gemini-backed question workflow during development.**
The final 87-second historical-match recording captured a real Gemini HTTP 200
answer through all three evidence tools on October 22, 2026. This is Microsoft orchestration
with a Google model, not Microsoft-hosted inference.

No Azure resources are provisioned. The separate Microsoft Foundry Azure OpenAI
v1 adapter has mocked HTTP tests but still needs a real deployment smoke check.
Template explanations make no model calls. The repository's GitHub Actions
workflow does not establish successful CI or Azure deployment.

## Component mapping

| Component | Current implementation | Proposed Microsoft integration |
| --- | --- | --- |
| Fixture selection and event replay | FastAPI, StatsBomb HTTP source, per-connection replay | Containerize and run in Azure Container Apps |
| Momentum and shot map data | Deterministic Python calculations | Run inside the same application container |
| Explanations and personalization | Optional Foundry adapter; casual/analyst modes, templates by default; live verification pending | Microsoft Foundry Azure OpenAI v1 chat completions |
| Match questions and tool use | Implemented Microsoft Agent Framework evidence/narration workflow with three read-only tools and Gemini inference | Retain the workflow; add authoritative server sessions and evaluate a Microsoft-hosted model integration separately |
| Viewer updates | Direct SSE, no resume | Optional Azure Web PubSub WebSockets for match/session groups |
| Observability | Not implemented | Application Insights traces, latency metrics, and errors |

The browser matchroom and broadcast-style overlay are implemented. The overlay
can start its own replay or join a matchroom in the same browser. The public app uses StatsBomb exclusively. See
[the demo guide](demo.md) for their capabilities and limits.

## Proposed implementation sequence

1. Validate the implemented local viewing experience with StatsBomb replay.
2. Configure the implemented Foundry provider using `.env`; use the README's
   fictional-data smoke check to verify deployment access. Keep the explicitly
   labeled template fallback for local development.
3. Extend the implemented shot-triggered explanations to other meaningful moments.
   Snapshot isolation, event references, casual/analyst modes, background inference,
   bounded requests, and failure fallbacks are already implemented.
4. Evaluate the implemented Agent Framework/Gemini workflow, provide usable
   provider access for judge testing, and verify Foundry separately before claiming
   Foundry inference. Provide reproducible setup and judge-access instructions.
5. Prepare and test a container image and deployment configuration. Deploy to
   Azure only when cloud hosting is needed; document resources and associated costs.

## Hosting work still required

Container Apps can host the FastAPI service, but this repository does not yet
include a Dockerfile, infrastructure templates, or a tested Azure deployment.
The documented HTTP ingress request timeout is 240 seconds. Full-match SSE needs
tested reconnection/resume, or an alternative delivery path such as Web PubSub.
The current endpoint starts from the beginning on reconnect.

Replay state currently belongs to a single connection/process. For shared match
rooms or recovery across replicas, design a replay worker, sequenced updates,
snapshots, and group/session isolation before enabling horizontal scaling.

Keep service credentials in environment variables or the hosting platform's
secret/identity facilities. A browser must never receive a Foundry credential.
Do not add deployment credentials to GitHub or the public demo.

## What the rules establish

The [official rules](https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md)
describe a functioning project, not merely an architecture proposal:

- Section 4.3: the project must run and match its description/demo.
- Section 4.4: the pitch identifies Microsoft/Azure technologies actually used.
- Section 4.8: judge access may be a website, functioning demo, or test build.
  Azure hosting is not stated as a universal requirement.
- Section 6.1: the first judging stage checks theme and application of required
  technologies; section 6.2 scores the use of the featured technologies.
- Category descriptions require demonstrated Foundry usage or Azure integration
  when entering those respective categories.

Our interpretation: documenting future deployment is useful but does not prove
actual platform use. A local application with a working Microsoft integration
and an accessible test build is a possible route; eligibility and scoring remain
the judges' decision. A disabled integration tested only with mocks is not evidence
that the service actually works. We should demonstrate a real integration before
claiming it in the pitch.

The submission still needs a public repository, judge access with usable model
quota, and a public URL for the recorded demo under two minutes. Agent Framework
with Gemini has been exercised; real Foundry verification remains open. Casual/analyst personalization and
on-screen insights are implemented. The default app retains historical fixtures. The separate `pipenv run demo` build
exposes the seeded synthetic source on port 8012; see [judge instructions](judging.md).
Structural generator checks pass; independent football-realism evaluation remains open.

## References

- [Microsoft Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/what-is-ai-foundry)
- [Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/overview)
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/overview)
- [Container Apps ingress limits](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)
- [Azure Web PubSub](https://learn.microsoft.com/en-us/azure/azure-web-pubsub/overview)
- [Application Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable?tabs=python)
