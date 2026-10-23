import pytest

from app.analytics import MatchAnalytics
from app.peak_momentum import PeakMomentum


def action(identifier, seconds=0, team=1, period=1, **extra):
    return {
        "id": identifier,
        "period": period,
        "timestamp": f"00:{seconds // 60:02}:{seconds % 60:06.3f}",
        "minute": seconds // 60,
        "second": seconds % 60,
        "team": {"id": team},
        "type": {"name": "Carry"},
        "location": [5, 5],
        "carry": {"end_location": [115, 40]},
        **extra,
    }


def test_minute_peak_cap_not_action_sum_and_team_difference():
    model = PeakMomentum((1, 2))
    first = model.consume(action("a"), 0)
    assert first["home"] == 0.1
    assert model.consume(action("b"), 10)["home"] == pytest.approx(0.1)
    assert model.consume(action("c", team=2), 20)["net_difference"] == pytest.approx(0)


def test_weighting_includes_quiet_minutes_expires_and_resets_halves():
    model = PeakMomentum((1, 2))
    model.consume(action("a"), 0)

    def quiet(identifier, period=1):
        return action(identifier, period=period, type={"name": "Pressure"})

    assert model.consume(quiet("q1"), 60)["home"] == pytest.approx(0.1 / 3)
    assert model.consume(quiet("q2"), 240)["home"] == 0
    model.consume(action("b"), 250)
    assert model.consume(quiet("q3", 2), 0)["home"] == 0


def test_shots_use_start_threat_and_failed_passes_do_not_add_peaks():
    model = PeakMomentum((1, 2))
    failed = action(
        "fail",
        type={"name": "Pass"},
        **{"pass": {"end_location": [115, 40], "outcome": {"name": "Incomplete"}}},
    )
    assert model.consume(failed, 0)["home"] == 0
    shot = action("shot", type={"name": "Shot"}, location=[115, 40])
    assert model.consume(shot, 1)["home"] == 0.1
    assert model.consume(action("shootout", period=5), 0)["home"] == 0


def test_peak_momentum_is_duplicate_safe_and_persists_between_actions():
    state = MatchAnalytics(1, 2)
    first = state.consume(action("a"))
    assert first["momentum"]["home"] > 0
    assert "peak_momentum" not in first
    assert state.consume(action("a"))["momentum"] == first["momentum"] | {"action_value": None}
    quiet = state.consume(action("b", seconds=15, type={"name": "Pressure"}))
    assert quiet["momentum"]["home"] == pytest.approx(first["momentum"]["home"])


def test_backward_home_move_does_not_assign_threat_to_away():
    model = PeakMomentum((1, 2))
    result = model.consume(action("back", location=[115, 40], carry={"end_location": [50, 40]}), 0)
    assert result["home"] > 0
    assert result["away"] == 0
    assert result["net_difference"] > 0


def test_missing_locations_leave_window_gaps_and_expire():
    model = PeakMomentum((1, 2))
    missing = action("missing", carry={"end_location": None})
    assert model.consume(missing, 0)["net_difference"] is None
    assert model.consume(action("valid"), 20)["status"] == "incomplete"
    resolved = model.consume(action("quiet", type={"name": "Pressure"}), 240)
    assert resolved["status"] == "available"
    assert resolved["net_difference"] == 0


def test_repeated_ids_do_not_recount_or_change_earlier_snapshot():
    model = PeakMomentum((1, 2))
    first = model.consume(action("first"), 0)
    model.consume(action("away", team=2), 10)
    repeated = model.consume(action("away", team=2), 10)
    assert repeated["source_values_seen"] == 2
    assert first["away"] == 0
    assert first["home"] == 0.1
