import asyncio
import json

import httpx
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.chat import ChatRequest, MatchChat
from app.config import Settings


def request():
    return ChatRequest(
        question="Who has created better chances?",
        snapshot={
            "clock": {"minute": 12, "second": 30},
            "events": [{"id": "seen", "minute": 12, "action": "Shot · Saved"}],
            "shot_summary": {"1": {"shots": 1, "xg": 0.2}},
        },
    )


def test_grounded_answer_uses_server_key_and_checks_citations():
    def handler(req):
        assert req.headers["x-goog-api-key"] == "test-key"
        payload = json.loads(req.content)
        assert payload["store"] is False
        assert payload["generation_config"]["thinking_level"] == "low"
        assert "historical match knowledge" in payload["system_instruction"]
        assert json.loads(payload["input"])["snapshot"]["events"][0]["id"] == "seen"
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(
                                    {
                                        "text": "The only recorded shot was worth 0.2 xG.",
                                        "evidence_event_ids": ["seen"],
                                    }
                                ),
                            }
                        ],
                    }
                ],
            },
        )

    chat = MatchChat(Settings(gemini_api_key="test-key"), httpx.MockTransport(handler))
    answer = asyncio.run(chat.ask(request()))
    assert answer["evidence"][0]["id"] == "seen"
    assert answer["as_of"] == {"minute": 12, "second": 30}
    assert "test-key" not in json.dumps(answer)


@pytest.mark.parametrize("status,expected", [(400, 502), (403, 503), (429, 429), (500, 502)])
def test_upstream_errors_are_sanitized(status, expected):
    chat = MatchChat(
        Settings(gemini_api_key="test-key"),
        httpx.MockTransport(
            lambda req: httpx.Response(status, json={"error": {"message": "secret upstream text"}})
        ),
    )
    with pytest.raises(HTTPException) as error:
        asyncio.run(chat.ask(request()))
    assert error.value.status_code == expected
    assert "secret" not in error.value.detail


def test_future_or_invented_citation_is_rejected():
    chat = MatchChat(
        Settings(gemini_api_key="test-key"),
        httpx.MockTransport(
            lambda req: httpx.Response(
                200,
                json={
                    "outputs": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "text": "An unsupported claim.",
                                    "evidence_event_ids": ["future"],
                                }
                            ),
                        }
                    ]
                },
            )
        ),
    )
    with pytest.raises(HTTPException) as error:
        asyncio.run(chat.ask(request()))
    assert error.value.status_code == 502


def test_missing_key_and_context_limits():
    with pytest.raises(HTTPException) as error:
        asyncio.run(MatchChat(Settings(gemini_api_key="")).ask(request()))
    assert error.value.status_code == 503
    with pytest.raises(ValidationError):
        ChatRequest(question="hello", snapshot={"events": [{}] * 61})
    with pytest.raises(ValidationError):
        ChatRequest(question="hello", snapshot={"text": "a" * 60001})


@pytest.mark.parametrize("failure", ["connection", "service"])
def test_transient_failures_are_retried(failure, monkeypatch):
    calls = []

    async def no_wait(seconds):
        pass

    monkeypatch.setattr("app.chat.asyncio.sleep", no_wait)

    def handler(req):
        calls.append(req)
        if len(calls) < 3:
            if failure == "connection":
                raise httpx.ConnectError("connection interrupted", request=req)
            return httpx.Response(503)
        return httpx.Response(
            200,
            json={
                "outputs": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "text": "One shot worth 0.2 xG is recorded.",
                                "evidence_event_ids": ["seen"],
                            }
                        ),
                    }
                ]
            },
        )

    chat = MatchChat(Settings(gemini_api_key="test-key"), httpx.MockTransport(handler))
    assert asyncio.run(chat.ask(request()))["evidence_event_ids"] == ["seen"]
    assert len(calls) == 3


def test_persistent_network_failure_has_distinct_sanitized_error(monkeypatch):
    calls = []

    async def no_wait(seconds):
        pass

    monkeypatch.setattr("app.chat.asyncio.sleep", no_wait)

    def handler(req):
        calls.append(req)
        raise httpx.ConnectError("secret upstream text", request=req)

    chat = MatchChat(Settings(gemini_api_key="test-key"), httpx.MockTransport(handler))
    with pytest.raises(HTTPException) as error:
        asyncio.run(chat.ask(request()))
    assert len(calls) == 3
    assert "internet or proxy" in error.value.detail
    assert "secret" not in error.value.detail


def test_framework_tools_keep_questions_isolated_and_label_player_window():
    from app.chat_workflow import run_match_workflow

    contexts = []

    async def generate(context):
        contexts.append(context)
        return {"text": "Grounded answer", "provider": "Gemini"}

    async def run():
        requests = [
            {
                "question": "Who is involved?",
                "snapshot": {
                    "clock": {"minute": minute},
                    "stats": {"tackles": minute},
                    "events": [{"id": str(minute)}],
                    "passing_network": {"home": {"players": [{"name": name}]}},
                    "untrusted_extra": "Never forward arbitrary fields",
                },
            }
            for minute, name in [(10, "Alice"), (20, "Bob")]
        ]
        results = await asyncio.gather(*(run_match_workflow(item, generate) for item in requests))
        for result in results:
            assert result["orchestrator"] == "Microsoft Agent Framework"
            assert result["tools_used"] == [
                "get_match_stats",
                "get_recent_events",
                "get_player_summary",
            ]
        for context in contexts:
            snapshot = context["snapshot"]
            minute = snapshot["clock"]["minute"]
            assert snapshot["events"] == [{"id": str(minute)}]
            assert snapshot["stats"]["tackles"] == minute
            summary = snapshot["player_summary"]
            assert "Not full-match player totals" in summary["scope"]
            assert summary["teams"]["home"]["players"][0]["name"] == (
                "Alice" if minute == 10 else "Bob"
            )
            assert "untrusted_extra" not in snapshot
        assert "player_summary" not in requests[0]["snapshot"]

    asyncio.run(run())
