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

    def quiet(period=1):
        return action("quiet", period=period, type={"name": "Pressure"})

    assert model.consume(quiet(), 60)["home"] == pytest.approx(0.1 / 3)
    assert model.consume(quiet(), 240)["home"] == 0
    model.consume(action("b"), 250)
    assert model.consume(quiet(2), 0)["home"] == 0


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


def test_per_action_progression_is_duplicate_safe():
    state = MatchAnalytics(1, 2)
    first = state.consume(action("a"))
    assert first["momentum"]["home"] > 0
    assert "peak_momentum" not in first
    assert state.consume(action("a"))["momentum"] == first["momentum"] | {"action_value": None}
    quiet = state.consume(action("b", seconds=15, type={"name": "Pressure"}))
    assert quiet["momentum"]["home"] == 0
