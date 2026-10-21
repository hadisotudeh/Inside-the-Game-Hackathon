"""Experimental minute-peak xT proxy, independent of progression momentum."""

from app.xt import GRID, cell, movement


class PeakMomentum:
    def __init__(self, team_ids):
        self.team_ids = team_ids
        self.period = None
        self.peaks = {}

    def consume(self, event, now):
        if event["period"] != self.period:
            self.period = event["period"]
            self.peaks.clear()
        minute = int(now // 60)
        team = (event.get("team") or {}).get("id")
        location = None
        move = movement(event)
        if move is not None:
            location = move[1]
        elif event["type"]["name"] == "Shot":
            location = event.get("location")
        index = cell(location)
        if team in self.team_ids and index is not None and self.period != 5:
            peak = min(0.1, max(0.0, GRID[index[0]][index[1]]))
            key = (minute, team)
            self.peaks[key] = max(self.peaks.get(key, 0.0), peak)
        self.peaks = {key: value for key, value in self.peaks.items() if key[0] >= minute - 3}
        buckets = range(max(0, minute - 3), minute + 1)
        weights = {bucket: 2 ** (-(now - bucket * 60) / 60) for bucket in buckets}
        denominator = sum(weights.values())
        values = [
            sum(self.peaks.get((bucket, t), 0.0) * weight for bucket, weight in weights.items())
            / denominator
            for t in self.team_ids
        ]
        return {
            "home": values[0],
            "away": values[1],
            "net_difference": values[0] - values[1],
            "metric": "peak_xt_proxy",
            "cap": 0.1,
            "window_minutes": 4,
            "half_life_seconds": 60,
        }
