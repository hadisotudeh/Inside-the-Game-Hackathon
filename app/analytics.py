"""Incremental, deterministic event analytics in StatsBomb's 120 x 80 coordinates."""

from copy import deepcopy
from math import isfinite

from app.passing import PassingNetworks
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
    def __init__(self, home_id: int, away_id: int):
        self.team_ids = (home_id, away_id)
        self.period = None
        self.totals = {team: 0.0 for team in self.team_ids}
        self.counts = {team: 0 for team in self.team_ids}
        self.last_time = None
        self.values_seen = 0
        self.missing = set()
        self.seen = set()
        self.shots = []
        self.score = {str(team): 0 for team in self.team_ids}
        self.possession_seconds = {team: 0.0 for team in self.team_ids}
        self.possession_previous = None
        self.passing_networks = PassingNetworks(self.team_ids)
        self.match_stats = {
            team: {
                "passes": 0,
                "completed_passes": 0,
                "shots_on_target": 0,
                "final_third_passes": 0,
                "corners": 0,
                "tackles": 0,
            }
            for team in self.team_ids
        }

    def consume(self, event: dict) -> dict:
        now = period_seconds(event)
        period = event["period"]
        if event["id"] not in self.seen:
            self.totals = {team: 0.0 for team in self.team_ids}
            self.missing.clear()
            previous = self.possession_previous
            if previous is not None and previous[0] == period and period != 5:
                _, previous_time, owner = previous
                if owner in self.possession_seconds:
                    self.possession_seconds[owner] += max(0, now - previous_time)
            owner = (event.get("possession_team") or {}).get("id")
            # Do not count the wait for a restart after an explicit stoppage.
            if event.get("out") or event["type"]["name"] in {
                "Half End",
                "Injury Stoppage",
                "Referee Ball-Drop",
                "Foul Committed",
                "Offside",
            }:
                owner = None
            previous_time = previous[1] if previous and previous[0] == period else now
            self.possession_previous = (period, max(now, previous_time), owner)
        if self.period != period:
            self.totals = {team: 0.0 for team in self.team_ids}
            self.counts = {team: 0 for team in self.team_ids}
            self.missing.clear()
            self.last_time = None
            self.period = period
        now = max(now, self.last_time if self.last_time is not None else now)
        self.last_time = now
        action_value = None
        added_shot = None
        if event["id"] not in self.seen:
            self.totals = {team: 0.0 for team in self.team_ids}
            self.missing.clear()
            self.seen.add(event["id"])
            self.passing_networks.consume(event)
            team = event.get("team", {}).get("id")
            if team in self.team_ids and period != 5:
                self.consume_match_stats(event, team)
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
        possession_total = sum(self.possession_seconds.values())
        final_third_total = sum(stats["final_third_passes"] for stats in self.match_stats.values())
        result = {
            "passing_network": self.passing_networks.snapshot(),
            "match_stats": {
                str(team): {
                    **stats,
                    "field_tilt": (
                        100 * stats["final_third_passes"] / final_third_total
                        if final_third_total
                        else None
                    ),
                    "pass_completion": (
                        100 * stats["completed_passes"] / stats["passes"]
                        if stats["passes"]
                        else None
                    ),
                }
                for team, stats in self.match_stats.items()
            },
            "possession": {
                "method": "event_time",
                "seconds": {str(team): value for team, value in self.possession_seconds.items()},
                "percentages": {
                    str(team): value / possession_total * 100 if possession_total else None
                    for team, value in self.possession_seconds.items()
                },
            },
            "score": dict(self.score),
            "momentum": {
                "period": period,
                "period_seconds": now,
                "action_value": action_value,
                "metric": "xt",
                "model": MODEL_ID,
                "missing_movements": len(self.missing),
                "aggregation": "per_action",
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

    def consume_match_stats(self, event: dict, team: int) -> None:
        stats = self.match_stats[team]
        kind = event["type"]["name"]
        if kind == "Pass":
            details = event.get("pass", {})
            stats["passes"] += 1
            stats["completed_passes"] += not details.get("outcome")
            stats["corners"] += details.get("type", {}).get("name") == "Corner"
        if kind == "Duel" and event.get("duel", {}).get("type", {}).get("name") == "Tackle":
            stats["tackles"] += 1
        if kind == "Shot":
            outcome = event.get("shot", {}).get("outcome", {}).get("name")
            stats["shots_on_target"] += outcome in {"Goal", "Saved", "Saved to Post"}
        if kind != "Pass" or event.get("pass", {}).get("outcome"):
            return
        location = event.get("location")
        if not isinstance(location, (list, tuple)) or len(location) < 2:
            return
        if any(
            isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v)
            for v in location[:2]
        ):
            return
        x, y = location[:2]
        # Both teams' raw StatsBomb coordinates face +x, including after halftime.
        stats["final_third_passes"] += 80 <= x <= 120 and 0 <= y <= 80
