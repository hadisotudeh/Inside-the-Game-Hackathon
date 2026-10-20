import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.explanations import ExplanationProvider
from app.main import create_app
from app.replay import replay

MATCH = {
    "match_id": 10,
    "home_team": {"id": 1, "name": "Home"},
    "away_team": {"id": 2, "name": "Away"},
}


def shot(identifier):
    return {
        "id": str(identifier),
        "index": identifier,
        "period": 1,
        "timestamp": "00:00:00.000",
        "minute": 0,
        "second": 0,
        "type": {"name": "Shot"},
        "team": {"id": 1},
        "location": [100, 40],
        "shot": {"statsbomb_xg": 0.2, "outcome": {"name": "Saved"}},
    }


def snapshot():
    return {
        "event": {"id": "1"},
        "teams": [MATCH["home_team"], MATCH["away_team"]],
        "shot_added": {"event_id": "1", "team_id": 1, "outcome": "Saved", "xg": 0.2},
        "momentum": {"status": "unavailable", "home": None, "away": None, "net_difference": None},
        "shot_summary": {"1": {"shots": 1, "xg": 0.2}},
    }


def settings(**overrides):
    return Settings(
        _env_file=None,
        **{
            "explanation_provider": "foundry",
            "foundry_endpoint": "https://example.openai.azure.com",
            "foundry_deployment": "my-deployment",
            "foundry_api_key": "test-key",
            **overrides,
        },
    )


def response(text="A saved shot for Home.", evidence=None, finish="stop"):
    return {
        "choices": [
            {
                "finish_reason": finish,
                "message": {
                    "content": json.dumps(
                        {
                            "text": text,
                            "evidence_event_ids": evidence or ["1"],
                        }
                    )
                },
            }
        ]
    }


def test_foundry_request_and_validated_response():
    def handler(request):
        assert str(request.url) == "https://example.openai.azure.com/openai/v1/chat/completions"
        assert request.headers["api-key"] == "test-key"
        body = json.loads(request.content)
        assert body["model"] == "my-deployment"
        assert body["response_format"]["json_schema"]["strict"] is True
        assert json.loads(body["messages"][1]["content"])["snapshot"] == snapshot()
        return httpx.Response(200, json=response())

    provider = ExplanationProvider(settings(), httpx.MockTransport(handler))
    result = asyncio.run(provider.explain(snapshot(), "analyst"))
    assert result["provider"] == "microsoft_foundry"
    assert result["ai_generated"] is True
    assert result["evidence_event_ids"] == ["1"]
    assert "test-key" not in json.dumps(result)


@pytest.mark.parametrize(
    "payload", [response(evidence=["future"]), response(finish="length"), {}, response(text=" ")]
)
def test_bad_response_falls_back(payload):
    provider = ExplanationProvider(
        settings(),
        httpx.MockTransport(
            lambda request: httpx.Response(200, json=payload),
        ),
    )
    result = asyncio.run(provider.explain(snapshot(), "casual"))
    # Blank output should also be rejected rather than shown as an empty overlay.
    assert result["provider"] == "template"
    assert result["ai_generated"] is False
    assert result["fallback_reason"] == "invalid_response"


def test_service_error_and_timeout_fallback():
    provider = ExplanationProvider(
        settings(),
        httpx.MockTransport(
            lambda request: httpx.Response(429, text="private service details"),
        ),
    )
    result = asyncio.run(provider.explain(snapshot(), "analyst"))
    assert result["fallback_reason"] == "service_error"
    assert "private" not in json.dumps(result)

    async def slow(request):
        await asyncio.sleep(1)
        return httpx.Response(200, json=response())

    provider = ExplanationProvider(
        settings(explanation_timeout_seconds=0.01), httpx.MockTransport(slow)
    )
    assert asyncio.run(provider.explain(snapshot(), "casual"))["fallback_reason"] == "timeout"


def test_local_mode_and_configuration():
    provider = ExplanationProvider(settings(explanation_provider="template"))
    casual = asyncio.run(provider.explain(snapshot(), "casual"))
    analyst = asyncio.run(provider.explain(snapshot(), "analyst"))
    assert casual["text"] != analyst["text"]
    assert casual["ai_generated"] is False
    with pytest.raises(ValidationError):
        settings(foundry_api_key="")
    with pytest.raises(ValidationError):
        settings(foundry_endpoint="http://example.com")
    with pytest.raises(ValidationError):
        settings(foundry_endpoint="https://example.com/openai/v1")
    assert "test-key" not in repr(settings())


def test_slow_explanation_does_not_block_replay_or_see_future_shots():
    async def collect():
        release = asyncio.Event()
        snapshots = []

        async def handler(request):
            snapshots.append(json.loads(request.content)["messages"][1]["content"])
            await release.wait()
            return httpx.Response(200, json=response())

        async def connected():
            return False

        provider = ExplanationProvider(
            settings(explanation_interval_seconds=0), httpx.MockTransport(handler)
        )
        frames = []
        async for frame in replay([shot(1), shot(2)], MATCH, 1000, connected, provider):
            frames.append(frame)
            if '"index": 2' in frame:
                # Second event arrives while inference for the first shot is still pending.
                assert not any("event: insight" in f for f in frames)
                release.set()
        assert len(snapshots) == 1
        supplied = json.loads(snapshots[0])["snapshot"]
        assert supplied["shot_summary"]["1"]["shots"] == 1
        assert supplied["shot_added"]["event_id"] == "1"
        assert "event: insight" in frames[-2]
        assert "event: complete" in frames[-1]

    asyncio.run(collect())


def test_disabled_and_zero_budget_make_no_requests():
    async def collect(mode, budget):
        async def connected():
            return False

        def handler(request):
            raise AssertionError("No request expected")

        provider = ExplanationProvider(
            settings(explanation_provider=mode, explanation_max_calls=budget),
            httpx.MockTransport(handler),
        )
        return [frame async for frame in replay([shot(1)], MATCH, 1, connected, provider)]

    for mode, budget in [("off", 12), ("foundry", 0)]:
        assert not any("event: insight" in f for f in asyncio.run(collect(mode, budget)))


def test_closing_stream_cancels_inference():
    async def check():
        started = asyncio.Event()
        cancelled = asyncio.Event()

        async def handler(request):
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        async def connected():
            return False

        provider = ExplanationProvider(settings(), httpx.MockTransport(handler))
        stream = replay([shot(1), shot(2)], MATCH, 1, connected, provider)
        await anext(stream)  # metadata
        await anext(stream)  # first shot
        await anext(stream)  # schedule inference, then emit second shot
        await started.wait()
        await stream.aclose()
        assert cancelled.is_set()

    asyncio.run(check())


def test_api_opt_in_insights_and_audience(monkeypatch):
    monkeypatch.setenv("GAME_EXPLANATION_PROVIDER", "template")
    app = create_app()

    class Source:
        async def matches(self):
            return [MATCH]

        async def events(self, match_id):
            return [shot(1)]

    app.state.source = Source()
    with TestClient(app) as client:
        assert "event: insight" not in client.get("/matches/10/stream").text
        response = client.get("/matches/10/stream?insights=true&audience=analyst")
        payloads = [
            json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")
        ]
        insight = next(p for p in payloads if "ai_generated" in p)
        assert insight["provider"] == "template"
        assert insight["audience"] == "analyst"
        assert insight["as_of_event_id"] == "1"
        assert client.get("/matches/10/stream?audience=unknown").status_code == 422
