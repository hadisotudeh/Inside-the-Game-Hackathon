import pytest

from app.analytics import MatchAnalytics


def event(identifier, kind="Pass", team=1, period=1, **extra):
    return {
        "id": identifier,
        "type": {"name": kind},
        "team": {"id": team},
        "period": period,
        "minute": 60,
        "second": 0,
        "timestamp": "00:15:00.000",
        "player": {"id": 10, "name": "Passer"},
        "location": [40, 20],
        "pass": {"recipient": {"id": 11, "name": "Receiver"}, "end_location": [80, 60]},
        **extra,
    }


def test_network_averages_links_lineup_numbers_and_duplicates():
    state = MatchAnalytics(1, 2)
    state.consume(
        event(
            "lineup",
            "Starting XI",
            tactics={"lineup": [{"player": {"id": 10, "name": "Passer"}, "jersey_number": 7}]},
        )
    )
    first = event("a")
    state.consume(first)
    state.consume(first)
    result = state.consume(
        event(
            "b",
            player={"id": 11, "name": "Receiver"},
            location=[100, 50],
            **{"pass": {"recipient": {"id": 10, "name": "Passer"}, "end_location": [60, 30]}},
        )
    )
    network = result["passing_network"]["1"]
    assert network["passes"] == 2
    assert network["links"] == [{"source": 10, "target": 11, "passes": 2}]
    players = {p["id"]: p for p in network["players"]}
    assert players[10]["x"] == pytest.approx(50)
    assert players[10]["y"] == pytest.approx(25)
    assert players[10]["jersey_number"] == 7
    assert players[11]["involvements"] == 2
    assert result["passing_network"]["2"]["players"] == []


def test_substitution_resets_only_affected_team_and_excludes_departed_player():
    state = MatchAnalytics(1, 2)
    state.consume(event("a"))
    state.consume(event("b", team=2))
    sub = event(
        "sub", "Substitution", substitution={"replacement": {"id": 12, "name": "Substitute"}}
    )
    result = state.consume(sub)["passing_network"]
    assert result["1"]["passes"] == 0
    assert result["1"]["reason"] == "Substitution"
    assert result["1"]["since"] == {"minute": 60, "second": 0}
    assert result["2"]["passes"] == 1
    state.consume(event("departed"))
    result = state.consume(event("new", player={"id": 12, "name": "Substitute"}))[
        "passing_network"
    ]["1"]
    assert result["passes"] == 1
    assert {p["id"] for p in result["players"]} == {11, 12}
    # A duplicate substitution cannot reset new passes.
    assert state.consume(sub)["passing_network"]["1"]["passes"] == 1


def test_network_exclusions_half_changes_and_dismissals():
    state = MatchAnalytics(1, 2)
    state.consume(event("a"))
    state.consume(event("second_half", period=2))
    state.consume(event("failed", **{"pass": {"outcome": {"name": "Incomplete"}}}))
    state.consume(event("missing", **{"pass": {"end_location": [80, 40]}}))
    state.consume(event("invalid", location=[float("nan"), 40]))
    state.consume(event("shootout", period=5))
    result = state.consume(event("pressure", "Pressure"))["passing_network"]["1"]
    assert result["passes"] == 2
    result = state.consume(
        event("red", "Bad Behaviour", bad_behaviour={"card": {"name": "Red Card"}})
    )["passing_network"]["1"]
    assert result["players"] == []
    assert result["reason"] == "Sending-off"
    assert state.consume(event("after_red"))["passing_network"]["1"]["passes"] == 0
