import asyncio
import json

import httpx
import pytest
from fastapi import HTTPException

from app.chat import ChatRequest, MatchChat
from app.config import Settings


@pytest.mark.parametrize(
    "citation,finish,expected",
    [("seen", "stop", 200), ("future", "stop", 502), ("seen", "length", 502)],
)
def test_foundry_grounding_and_complete_output(citation, finish, expected):
    def handler(request):
        assert str(request.url) == "https://example.openai.azure.com/openai/v1/chat/completions"
        assert request.headers["api-key"] == "azure-secret"
        payload = json.loads(request.content)
        assert payload["model"] == "touchline-chat"
        assert payload["response_format"]["json_schema"]["strict"] is True
        assert payload["store"] is False
        assert "historical match knowledge" in payload["messages"][0]["content"]
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": finish,
                        "message": {
                            "content": json.dumps(
                                {"text": "A shot was recorded.", "evidence_event_ids": [citation]}
                            )
                        },
                    }
                ]
            },
        )

    settings = Settings(
        chat_provider="foundry",
        foundry_endpoint="https://example.openai.azure.com",
        foundry_deployment="touchline-chat",
        foundry_api_key="azure-secret",
    )
    chat = MatchChat(settings, httpx.MockTransport(handler))
    request = ChatRequest(question="What happened?", snapshot={"events": [{"id": "seen"}]})
    if expected == 200:
        answer = asyncio.run(chat.ask(request))
        assert answer["provider"] == "Microsoft Foundry"
        assert answer["orchestrator"] == "Microsoft Agent Framework"
        assert answer["evidence"][0]["id"] == "seen"
        assert "azure-secret" not in json.dumps(answer)
    else:
        with pytest.raises(HTTPException) as error:
            asyncio.run(chat.ask(request))
        assert error.value.status_code == expected
