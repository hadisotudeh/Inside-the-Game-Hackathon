import pytest

from app.analytics import MatchAnalytics


def action(identifier, seconds, owner=None, period=1, **extra):
    return {
        "id": identifier,
        "period": period,
        "timestamp": f"00:00:{seconds:06.3f}",
        "minute": 0,
        "second": int(seconds),
        "type": {"name": "Pressure"},
        "team": {"id": 2},
        "possession_team": {"id": owner} if owner else None,
        **extra,
    }


def test_possession_uses_time_and_possession_owner_not_event_team():
    state = MatchAnalytics(1, 2)
    assert state.consume(action("a", 0, 1))["possession"]["percentages"]["1"] is None
    state.consume(action("b", 30, 2))
    result = state.consume(action("c", 40, 2))["possession"]
    assert result["seconds"] == {"1": 30, "2": 10}
    assert result["percentages"] == {"1": 75, "2": 25}
    assert state.consume(action("c", 40, 2))["possession"] == result


def test_possession_excludes_stoppages_period_breaks_and_shootout():
    state = MatchAnalytics(1, 2)
    state.consume(action("a", 0, 1))
    state.consume(action("b", 10, 1, out=True))
    state.consume(action("c", 30, 2))
    state.consume(action("d", 40, 2))
    state.consume(action("e", 0, 1, period=2))
    result = state.consume(action("f", 10, 1, period=2))["possession"]
    assert result["seconds"] == {"1": 20, "2": 10}
    assert result["percentages"]["1"] == pytest.approx(200 / 3)
    state.consume(action("g", 0, 2, period=5))
    assert state.consume(action("h", 50, 2, period=5))["possession"] == result


def test_missing_possession_owner_is_not_assigned_to_event_team():
    state = MatchAnalytics(1, 2)
    state.consume(action("a", 0))
    result = state.consume(action("b", 30))["possession"]
    assert result["seconds"] == {"1": 0, "2": 0}
    assert result["percentages"] == {"1": None, "2": None}
