import pytest

from app.analytics import MatchAnalytics


def event(identifier, kind, team=1, period=1, **extra):
    return {
        "id": identifier,
        "period": period,
        "timestamp": "00:00:00.000",
        "minute": 0,
        "second": 0,
        "type": {"name": kind},
        "team": {"id": team},
        **extra,
    }


def test_pass_completion_corners_duplicates_and_cumulative_halves():
    state = MatchAnalytics(1, 2)
    assert (
        state.consume(event("start", "Half Start"))["match_stats"]["1"]["pass_completion"] is None
    )
    first = event("p1", "Pass", **{"pass": {"end_location": [80, 40]}})
    state.consume(first)
    state.consume(first)
    state.consume(event("p2", "Pass", **{"pass": {"outcome": {"name": "Incomplete"}}}))
    result = state.consume(event("p3", "Pass", period=2, **{"pass": {"type": {"name": "Corner"}}}))
    stats = result["match_stats"]["1"]
    assert stats["passes"] == 3
    assert stats["completed_passes"] == 2
    assert stats["pass_completion"] == pytest.approx(200 / 3)
    assert stats["corners"] == 1
    assert result["match_stats"]["2"]["passes"] == 0
    stats["passes"] = 99
    assert state.match_stats[1]["passes"] == 3


def test_on_target_outcomes_and_shootout_exclusion():
    state = MatchAnalytics(1, 2)
    for i, outcome in enumerate(
        ["Goal", "Saved", "Saved to Post", "Saved Off Target", "Post", "Blocked", "Off T"]
    ):
        result = state.consume(event(str(i), "Shot", shot={"outcome": {"name": outcome}}))
    assert result["match_stats"]["1"]["shots_on_target"] == 3
    state.consume(event("shootout", "Shot", period=5, shot={"outcome": {"name": "Goal"}}))
    assert state.match_stats[1]["shots_on_target"] == 3


def test_field_tilt_counts_completed_attacking_third_passes_across_halves():
    state = MatchAnalytics(1, 2)
    assert state.consume(event("start", "Half Start"))["match_stats"]["1"]["field_tilt"] is None
    first = event("home1", "Pass", location=[80, 0])
    state.consume(first)
    state.consume(first)
    state.consume(event("home2", "Pass", location=[100, 40]))
    result = state.consume(event("away", "Pass", team=2, period=2, location=[120, 80]))
    assert result["match_stats"]["1"]["final_third_passes"] == 2
    assert result["match_stats"]["2"]["final_third_passes"] == 1
    assert result["match_stats"]["1"]["field_tilt"] == pytest.approx(200 / 3)
    assert result["match_stats"]["2"]["field_tilt"] == pytest.approx(100 / 3)


def test_field_tilt_excludes_failed_passes_other_actions_invalid_locations_and_shootout():
    state = MatchAnalytics(1, 2)
    state.consume(event("carry", "Carry", location=[110, 40]))
    state.consume(event("pressure", "Pressure", location=[110, 40]))
    for i, location in enumerate(
        [[79.9, 40], [121, 40], [90, 81], [90, -1], [float("nan"), 40], None]
    ):
        state.consume(event(str(i), "Pass", location=location))
    state.consume(
        event("failed", "Pass", location=[110, 40], **{"pass": {"outcome": {"name": "Incomplete"}}})
    )
    result = state.consume(event("shootout", "Pass", period=5, location=[110, 40]))
    assert result["match_stats"]["1"]["final_third_passes"] == 0
    assert result["match_stats"]["1"]["field_tilt"] is None


def test_tackles_are_cumulative_and_not_inferred_from_recent_events():
    state = MatchAnalytics(1, 2)
    start = state.consume(event("start", "Half Start"))["match_stats"]
    assert start["1"]["tackles"] == start["2"]["tackles"] == 0
    tackle = event("tackle", "Duel", duel={"type": {"name": "Tackle"}})
    state.consume(tackle)
    state.consume(tackle)
    state.consume(event("aerial", "Duel", team=2, duel={"type": {"name": "Aerial Lost"}}))
    state.consume(event("pressure", "Pressure", team=2))
    later = state.consume(event("second_half", "Half Start", period=2))["match_stats"]
    assert later["1"]["tackles"] == 1
    assert later["2"]["tackles"] == 0
    result = state.consume(
        event("away_tackle", "Duel", team=2, period=2, duel={"type": {"name": "Tackle"}})
    )["match_stats"]
    assert result["2"]["tackles"] == 1
    result = state.consume(
        event("shootout", "Duel", team=2, period=5, duel={"type": {"name": "Tackle"}})
    )["match_stats"]
    assert result["2"]["tackles"] == 1
