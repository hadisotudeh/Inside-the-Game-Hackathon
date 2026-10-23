import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from app.analytics import MatchAnalytics
from app.main import create_app
from app.replay import replay


def event(identifier, second=0, period=1, kind="Shot", team=1, **extra):
    return {
        "id": identifier,
        "index": int(identifier),
        "period": period,
        "timestamp": f"00:00:{second:06.3f}",
        "minute": 0,
        "second": int(second),
        "type": {"name": kind},
        "team": {"id": team},
        "location": [100, 40],
        "shot": {"statsbomb_xg": 0.2, "outcome": {"name": "Goal"}},
        **extra,
    }


def test_incremental_shots_duplicates_and_period_reset():
    state = MatchAnalytics(1, 2)
    first = state.consume(event("1"))
    assert first["shot_summary"]["1"] == {"shots": 1, "xg": 0.2}
    assert first["momentum"]["net_difference"] == pytest.approx(0.1)
    assert state.consume(event("1"))["shot_added"] is None
    state.consume(event("2", kind="Carry", carry={"end_location": [115, 40]}))
    assert state.consume(event("3", second=30, kind="Pressure"))["momentum"][
        "home"
    ] == pytest.approx(0.1)
    reset = state.consume(event("4", period=2, kind="Half Start"))
    assert reset["momentum"]["home"] == 0
    assert reset["shot_summary"]["1"]["shots"] == 1


def test_shot_snapshots_preserve_recorded_players_and_handle_missing_frames():
    state = MatchAnalytics(1, 2)
    frame = [
        {
            "location": [118.4, 38.5],
            "player": {"id": 7, "name": "Keeper"},
            "position": {"id": 1, "name": "Goalkeeper"},
            "teammate": False,
        },
        {
            "location": [98, 11.3],
            "player": {"id": 8, "name": "Teammate"},
            "position": {"id": 17, "name": "Right Wing"},
            "teammate": True,
        },
        {"location": None, "player": {"id": 9}},
    ]
    shot = event(
        "1",
        shot={
            "statsbomb_xg": 0.2,
            "freeze_frame": frame,
            "end_location": [120, 40, 1],
            "outcome": {"name": "Saved"},
        },
    )
    result = state.consume(shot)
    players = result["shot_added"]["freeze_frame"]
    assert len(players) == 2
    assert players[0]["goalkeeper"] is True
    assert players[0]["teammate"] is False
    assert players[1]["goalkeeper"] is False
    assert players[1]["location"] == [98, 11.3]
    assert result["shot_added"]["end_location"] == [120, 40, 1]
    players[0]["location"][0] = 0
    assert state.shots[0]["freeze_frame"][0]["location"][0] == 118.4
    assert state.consume(event("2"))["shot_added"]["freeze_frame"] == []
    assert state.consume(event("3", kind="Pass"))["shot_added"] is None


def test_xt_signed_actions_and_missing_coordinates():
    state = MatchAnalytics(1, 2)
    move = event("1", kind="Carry", carry={"end_location": [115, 40]})
    result = state.consume(move)
    assert result["momentum"]["home"] == pytest.approx(0.1)
    assert result["momentum"]["action_value"] == pytest.approx(0.1494026)
    assert state.consume(move)["momentum"]["period_observations"]["1"] == 1
    result = state.consume(
        event("2", team=2, kind="Carry", location=[115, 40], carry={"end_location": [100, 40]})
    )
    assert result["momentum"]["away"] == pytest.approx(0.1)
    assert result["momentum"]["action_value"] == pytest.approx(-0.1494026)
    assert result["momentum"]["net_difference"] == 0
    result = state.consume(event("3", timestamp="00:01:00.000", kind="Pressure"))
    assert result["momentum"]["net_difference"] == 0
    result = state.consume(event("4", kind="Carry", timestamp="00:01:01.000"))
    assert result["momentum"]["status"] == "incomplete"
    assert result["momentum"]["home"] is None
    result = state.consume(event("5", period=5, kind="Carry", carry={"end_location": [115, 40]}))
    assert result["momentum"]["source_values_seen"] == 2


MATCH = {
    "match_id": 10,
    "home_team": {"id": 1, "name": "Home"},
    "away_team": {"id": 2, "name": "Away"},
}


class FakeSource:
    async def matches(self):
        return [MATCH]

    async def events(self, match_id):
        return [event("1", kind="Half Start"), event("2", second=0.001)]


def test_stream_is_incremental_and_sessions_are_independent():
    app = create_app()
    app.state.source = FakeSource()
    with TestClient(app) as client:
        assert client.get("/matches").json() == [MATCH]
        assert client.get("/matches/999/stream").status_code == 404
        assert client.get("/matches/10/stream?speed=0").status_code == 422
        assert client.get("/matches/10/stream?speed=nan").status_code == 422
        for _ in range(2):
            response = client.get("/matches/10/stream?speed=1000")
            assert response.headers["content-type"].startswith("text/event-stream")
            payloads = [
                json.loads(line[6:])
                for line in response.text.splitlines()
                if line.startswith("data: ")
            ]
            assert payloads[0]["simulated_live"] is True
            assert payloads[1]["shot_summary"]["1"]["shots"] == 0
            assert payloads[1]["momentum"]["status"] == "available"
            assert payloads[2]["momentum"]["net_difference"] == pytest.approx(0.1)
            assert payloads[2]["shot_added"]["event_id"] == "2"
            assert payloads[2]["shot_summary"]["1"]["shots"] == 1
            assert payloads[-1] == {"match_id": 10}


def test_replay_timing_preserves_period_clocks_and_skips_breaks(monkeypatch):
    clock = [0.0]
    waits = []

    async def sleep(delay):
        waits.append(delay)
        clock[0] += delay

    async def connected():
        return False

    monkeypatch.setattr("app.replay.time.monotonic", lambda: clock[0])
    monkeypatch.setattr("app.replay.asyncio.sleep", sleep)

    async def collect():
        events = [event("1"), event("2", second=20), event("3", period=2)]
        return [message async for message in replay(events, MATCH, 10, connected)]

    messages = asyncio.run(collect())
    assert sum(waits) == 2
    assert sum("event: update" in message for message in messages) == 3


def test_disconnected_replay_stops_before_processing():
    async def disconnected():
        return True

    async def collect():
        return [message async for message in replay([event("1")], MATCH, 1, disconnected)]

    messages = asyncio.run(collect())
    assert len(messages) == 1


def test_minute_peak_momentum_persists_then_expires_without_accumulation():
    state = MatchAnalytics(1, 2)
    first = state.consume(event("1", kind="Carry", carry={"end_location": [115, 40]}))
    value = first["momentum"]["home"]
    for identifier, second, _ in (("2", 15, 2), ("3", 30, 4), ("4", 45, 8)):
        result = state.consume(event(identifier, second=second, kind="Pressure"))
        assert result["momentum"]["home"] == pytest.approx(value)
        assert result["momentum"]["action_value"] is None
    assert first["momentum"]["aggregation"] == "trailing_minute_peaks"
    assert first["momentum"]["half_life_seconds"] == 60
    quiet = state.consume(event("5", timestamp="00:01:00.000", kind="Pressure"))
    assert quiet["momentum"]["home"] == pytest.approx(value / 3)
    expired = state.consume(event("6", timestamp="00:04:00.000", kind="Pressure"))
    assert expired["momentum"]["home"] == 0
