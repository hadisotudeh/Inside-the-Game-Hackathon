import asyncio

from fastapi.testclient import TestClient

from app.analytics import MatchAnalytics, period_seconds
from app.main import create_app
from app.synthetic import SyntheticSource


def test_synthetic_match_is_reproducible_and_consistent():
    source = SyntheticSource()
    events = asyncio.run(source.events(1))
    assert events == asyncio.run(source.events(1))
    assert len({event["id"] for event in events}) == len(events)
    assert [e["index"] for e in events] == list(range(1, len(events) + 1))
    state = MatchAnalytics(101, 202)
    for period in (1, 2):
        half = [e for e in events if e["period"] == period]
        assert half[0]["type"]["name"] == "Half Start"
        assert half[-1]["type"]["name"] == "Half End"
        assert [period_seconds(e) for e in half] == sorted(period_seconds(e) for e in half)
    for event in events:
        if "location" in event:
            assert 0 <= event["location"][0] <= 120
            assert 0 <= event["location"][1] <= 80
        state.consume(event)
    assert len(state.shots) > 10
    assert sum(state.score.values()) == sum(s["outcome"] == "Goal" for s in state.shots)


def test_score_counts_own_goals_once():
    events = asyncio.run(SyntheticSource().events(1))
    own_goal = {**events[0], "type": {"name": "Own Goal Against"}}
    state = MatchAnalytics(101, 202)
    state.consume(own_goal)
    state.consume(own_goal)
    assert state.score == {"101": 0, "202": 1}


def test_viewing_routes_use_statsbomb_only():
    app = create_app()

    class Source:
        async def matches(self):
            return [
                {
                    "match_id": 10,
                    "home_team": {"id": 33, "name": "Chelsea"},
                    "away_team": {"id": 1, "name": "Arsenal"},
                }
            ]

    app.state.source = Source()
    with TestClient(app) as client:
        html = client.get("/").text
        assert "Touchline — Match analysis" in html
        assert 'id="source"' not in html
        assert 'alt="StatsBomb"' in html
        overlay = client.get("/overlay")
        assert overlay.status_code == 200
        assert 'data-overlay="true"' in overlay.text
        assert 'id="homeScore"' in overlay.text
        assert 'id="awayScore"' in overlay.text
        assert client.get("/static/app.js").status_code == 200
        fixtures = client.get("/matches").json()
        assert fixtures[0]["home_team"]["name"] == "Chelsea"
        assert "home_score" not in fixtures[0]
        assert client.get("/matches/999/stream").status_code == 404
        schema = client.get("/openapi.json").json()
        for route in ("/matches", "/matches/{match_id}/stream"):
            assert not any(
                p["name"] == "source" for p in schema["paths"][route]["get"].get("parameters", [])
            )
        logos = client.get("/static/assets/teams.json").json()
        assert len(logos) == 20
        for team in logos.values():
            assert team["wikipedia"].startswith("https://en.wikipedia.org/wiki/")
            assert client.get(team["src"]).status_code == 200
