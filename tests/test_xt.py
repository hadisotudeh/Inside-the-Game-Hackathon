import pytest

from app.xt import action_xt, cell


def test_reference_grid_difference_and_coordinates():
    # Fixed reference cells from the published grid, not generated expectations.
    assert action_xt(
        {"type": {"name": "Carry"}, "location": [5, 5], "carry": {"end_location": [115, 5]}}
    ) == pytest.approx(0.0379259 - 0.00638303)
    assert cell([120, 80]) == (7, 11)
    assert cell([0, 0]) == (0, 0)
    for location in (None, [], [True, 4], [float("nan"), 4], [-1, 4], [121, 4]):
        assert cell(location) is None


def test_completed_pass_adapter_and_exclusions():
    event = {"type": {"name": "Pass"}, "location": [100, 40], "pass": {"end_location": [115, 40]}}
    assert action_xt(event) == pytest.approx(0.1494026)
    for reason in ("Incomplete", "Out", "Pass Offside", "Unknown"):
        assert action_xt({**event, "pass": {**event["pass"], "outcome": {"name": reason}}}) is None
    for restart in ("Corner", "Free Kick", "Goal Kick", "Kick Off", "Throw-in"):
        assert action_xt({**event, "pass": {**event["pass"], "type": {"name": restart}}}) is None
    assert action_xt({**event, "pass": {"end_location": [101, 41]}}) == 0
    assert action_xt({**event, "type": {"name": "Shot"}}) is None
