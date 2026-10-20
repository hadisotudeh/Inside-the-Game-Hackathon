"""Incremental, deterministic event analytics in StatsBomb's 120 x 80 coordinates."""

from copy import deepcopy
from math import isfinite

from app.xt import MODEL_ID, action_xt, movement


def shot_freeze_frame(shot: dict) -> list[dict]:
    """Keep recorded shot-time players; never infer missing positions."""
    players = []
    for entry in shot.get("freeze_frame") or []:
        location = entry.get("location")
        if not isinstance(location, list) or len(location) < 2:
            continue
        if not all(isinstance(v, (int, float)) and isfinite(v) for v in location[:2]):
            continue
        position = entry.get("position") or {}
        players.append(
            {
                "location": location[:2],
                "player": entry.get("player"),
                "position": position,
                "teammate": entry.get("teammate"),
                "goalkeeper": position.get("id") == 1 or position.get("name") == "Goalkeeper",
            }
        )
    return players


def period_seconds(event: dict) -> float:
    hours, minutes, seconds = event["timestamp"].split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


class MatchAnalytics:
    def __init__(self, home_id: int, away_id: int, half_life_seconds: float = 15):
        self.team_ids = (home_id, away_id)
        if half_life_seconds <= 0 or not isfinite(half_life_seconds):
            raise ValueError("half_life_seconds must be finite and positive")
        self.half_life_seconds = half_life_seconds
        self.period = None
        self.totals = {team: 0.0 for team in self.team_ids}
        self.counts = {team: 0 for team in self.team_ids}
        self.last_time = None
        self.values_seen = 0
        self.missing = set()
        self.seen = set()
        self.shots = []
        self.score = {str(team): 0 for team in self.team_ids}

    def consume(self, event: dict) -> dict:
        now = period_seconds(event)
        period = event["period"]
        if self.period != period:
            self.totals = {team: 0.0 for team in self.team_ids}
            self.counts = {team: 0 for team in self.team_ids}
            self.missing.clear()
            self.last_time = None
            self.period = period
        now = max(now, self.last_time if self.last_time is not None else now)
        decay = (
            2 ** (-(now - self.last_time) / self.half_life_seconds)
            if self.last_time is not None
            else 1
        )
        for team in self.team_ids:
            self.totals[team] *= decay
        self.last_time = now
        action_value = None
        added_shot = None
        if event["id"] not in self.seen:
            self.seen.add(event["id"])
            team = event.get("team", {}).get("id")
            if team in self.team_ids and period != 5:
                if event["type"]["name"] == "Own Goal Against":
                    opponent = next(t for t in self.team_ids if t != team)
                    self.score[str(opponent)] += 1
                elif (
                    event["type"]["name"] == "Shot"
                    and event.get("shot", {}).get("outcome", {}).get("name") == "Goal"
                ):
                    self.score[str(team)] += 1
            if team in self.team_ids and period != 5:
                value = action_xt(event)
                if value is not None:
                    self.totals[team] += value
                    self.counts[team] += 1
                    action_value = value
                    self.values_seen += 1
                elif movement(event) is not None:
                    self.missing.add(team)
            if event["type"]["name"] == "Shot" and team in self.team_ids:
                details = event["shot"]
                location = event.get("location")
                added_shot = {
                    "event_id": event["id"],
                    "team_id": team,
                    "player": event.get("player"),
                    "period": period,
                    "minute": event["minute"],
                    "second": event["second"],
                    "location": location,
                    "xg": details.get("statsbomb_xg"),
                    "outcome": details.get("outcome", {}).get("name"),
                    "body_part": details.get("body_part", {}).get("name"),
                    "shot_type": details.get("type", {}).get("name"),
                    "shootout": period == 5,
                    "freeze_frame": shot_freeze_frame(details),
                    "end_location": details.get("end_location"),
                }
                self.shots.append(added_shot)
        missing_teams = self.missing
        home, away = (
            None if team in missing_teams else self.totals[team] for team in self.team_ids
        )
        difference = home - away if home is not None and away is not None else None
        status = "available" if not missing_teams else "incomplete"
        result = {
            "score": dict(self.score),
            "momentum": {
                "period": period,
                "period_seconds": now,
                "half_life_seconds": self.half_life_seconds,
                "action_value": action_value,
                "metric": "xt",
                "model": MODEL_ID,
                "missing_movements": len(self.missing),
                "aggregation": "exponential_decay_sum",
                "status": status,
                "home": home,
                "away": away,
                "net_difference": difference,
                "period_observations": {str(team): self.counts[team] for team in self.team_ids},
                "source_values_seen": self.values_seen,
            },
            "shot_added": added_shot,
            "shot_summary": {
                str(team): {
                    "shots": sum(s["team_id"] == team and not s["shootout"] for s in self.shots),
                    "xg": round(
                        sum(
                            (s["xg"] or 0)
                            for s in self.shots
                            if s["team_id"] == team and not s["shootout"]
                        ),
                        4,
                    ),
                }
                for team in self.team_ids
            },
        }
        return deepcopy(result)
