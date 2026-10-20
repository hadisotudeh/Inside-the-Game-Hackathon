"""Explicit, potentially billable smoke check using a fictional match snapshot."""

import asyncio
import json

from app.analytics import MatchAnalytics
from app.config import Settings
from app.explanations import ExplanationProvider


async def check() -> bool:
    settings = Settings()
    if settings.explanation_provider != "foundry":
        print("Set GAME_EXPLANATION_PROVIDER=foundry and configure .env first.")
        return False
    event = {
        "id": "synthetic-smoke-shot-1",
        "index": 1,
        "period": 1,
        "timestamp": "00:10:00.000",
        "minute": 10,
        "second": 0,
        "type": {"name": "Shot"},
        "team": {"id": 1},
        "location": [100, 40],
        "shot": {"statsbomb_xg": 0.2, "outcome": {"name": "Saved"}},
    }
    snapshot = MatchAnalytics(1, 2).consume(event)
    snapshot["event"] = {"id": event["id"]}
    snapshot["teams"] = [{"id": 1, "name": "North FC"}, {"id": 2, "name": "South FC"}]
    result = await ExplanationProvider(settings).explain(snapshot, "analyst")
    print(json.dumps(result, indent=2))
    return result["provider"] == "microsoft_foundry"


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(check()) else 1)
