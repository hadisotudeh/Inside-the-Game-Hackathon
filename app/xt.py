"""Grid-based xT inference following socceraction.ExpectedThreat.rate (no interpolation).

Uses Karun Singh's public 12x8 surface recommended by socceraction.load_model.
StatsBomb coordinates already face the attacking goal; never apply display flips.
This is a direct event adapter, not the complete SPADL conversion pipeline.
"""

import json
from math import isfinite
from pathlib import Path

MODEL_ID = "karun-open-xt-12x8-v1"
GRID = json.loads((Path(__file__).parent / "models/open_xt_12x8_v1.json").read_text())


def cell(location):
    """StatsBomb top-left origin maps directly onto the model's top-left grid."""
    if not isinstance(location, (list, tuple)) or len(location) < 2:
        return None
    if any(
        isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v)
        for v in location[:2]
    ):
        return None
    x, y = location[:2]
    if not 0 <= x <= 120 or not 0 <= y <= 80:
        return None
    return min(7, int(y / 10)), min(11, int(x / 10))


def movement(event):
    """Select completed passes/crosses and recorded carries, excluding restarts."""
    kind = event.get("type", {}).get("name")
    if kind == "Pass":
        details = event.get("pass", {})
        # StatsBomb omits outcome for completed passes.
        if details.get("outcome") or details.get("type", {}).get("name") in {
            "Corner",
            "Free Kick",
            "Goal Kick",
            "Kick Off",
            "Throw-in",
        }:
            return None
    elif kind == "Carry":
        details = event.get("carry", {})
    else:
        return None
    return event.get("location"), details.get("end_location")


def action_xt(event):
    """Return signed end-cell minus start-cell threat, or None if not rateable."""
    move = movement(event)
    if move is None:
        return None
    start, end = (cell(location) for location in move)
    if start is None or end is None:
        return None
    return GRID[end[0]][end[1]] - GRID[start[0]][start[1]]
