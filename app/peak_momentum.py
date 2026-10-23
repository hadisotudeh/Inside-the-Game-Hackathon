"""Causal, minute-based attacking-threat proxy; not a scoring probability."""

from app.xt import GRID, cell, movement


class PeakMomentum:
    def __init__(self, team_ids):
        self.team_ids = team_ids
        self.period = None
        self.peaks = {}
        self.missing = set()
        self.seen = set()
        self.last = None
        self.values_seen = 0

    def consume(self, event, now):
        identifier = event.get("id")
        if identifier is not None and identifier in self.seen:
            return dict(self.last)
        if identifier is not None:
            self.seen.add(identifier)
        if event["period"] != self.period:
            self.period = event["period"]
            self.peaks.clear()
            self.missing.clear()
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
            self.values_seen += 1
            peak = min(0.1, max(0.0, GRID[index[0]][index[1]]))
            key = (minute, team)
            self.peaks[key] = max(self.peaks.get(key, 0.0), peak)
        elif (
            team in self.team_ids
            and self.period != 5
            and (move is not None or event["type"]["name"] == "Shot")
        ):
            self.missing.add((minute, team))
        self.peaks = {key: value for key, value in self.peaks.items() if key[0] >= minute - 3}
        self.missing = {key for key in self.missing if key[0] >= minute - 3}
        buckets = range(max(0, minute - 3), minute + 1)
        weights = {bucket: 2 ** (-(now - bucket * 60) / 60) for bucket in buckets}
        denominator = sum(weights.values())
        values = [
            min(
                0.1,
                max(
                    0.0,
                    sum(
                        self.peaks.get((bucket, t), 0.0) * weight
                        for bucket, weight in weights.items()
                    )
                    / denominator,
                ),
            )
            for t in self.team_ids
        ]
        missing_teams = {team for _, team in self.missing}
        home, away = [
            None if team in missing_teams else value
            for team, value in zip(self.team_ids, values, strict=True)
        ]
        self.last = {
            "home": home,
            "away": away,
            "net_difference": home - away if home is not None and away is not None else None,
            "metric": "peak_xt_proxy",
            "cap": 0.1,
            "window_minutes": 4,
            "half_life_seconds": 60,
            "aggregation": "trailing_minute_peaks",
            "status": "incomplete" if missing_teams else "available",
            "missing_movements": len(self.missing),
            "source_values_seen": self.values_seen,
        }
        return dict(self.last)
