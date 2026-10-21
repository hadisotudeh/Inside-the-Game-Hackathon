"""Live passing networks using only events already consumed by the replay."""

from math import isfinite


def valid_location(location):
    return (
        isinstance(location, (list, tuple))
        and len(location) >= 2
        and all(
            isinstance(v, (int, float)) and not isinstance(v, bool) and isfinite(v)
            for v in location[:2]
        )
        and 0 <= location[0] <= 120
        and 0 <= location[1] <= 80
    )


class PassingNetworks:
    def __init__(self, team_ids):
        self.teams = {
            team: {
                "roster": {},
                "removed": set(),
                "players": {},
                "links": {},
                "passes": 0,
                "since": None,
                "reason": "Kick-off",
            }
            for team in team_ids
        }

    def reset(self, state, event, reason):
        state["players"].clear()
        state["links"].clear()
        state["passes"] = 0
        state["since"] = {"minute": event["minute"], "second": event["second"]}
        state["reason"] = reason

    def consume(self, event):
        state = self.teams.get((event.get("team") or {}).get("id"))
        if state is None or event["period"] == 5:
            return
        kind = event["type"]["name"]
        if kind == "Starting XI":
            for entry in event.get("tactics", {}).get("lineup", []):
                player = entry.get("player") or {}
                if player.get("id") is not None:
                    state["roster"][player["id"]] = {
                        **player,
                        "jersey_number": entry.get("jersey_number"),
                    }
        elif kind == "Substitution":
            outgoing = event.get("player") or {}
            replacement = event.get("substitution", {}).get("replacement") or {}
            state["removed"].add(outgoing.get("id"))
            state["roster"].pop(outgoing.get("id"), None)
            if replacement.get("id") is not None:
                state["roster"][replacement["id"]] = replacement
            self.reset(state, event, "Substitution")
        elif kind in {"Bad Behaviour", "Foul Committed"}:
            details = event.get(
                "bad_behaviour" if kind == "Bad Behaviour" else "foul_committed", {}
            )
            if details.get("card", {}).get("name") in {"Red Card", "Second Yellow"}:
                player_id = (event.get("player") or {}).get("id")
                state["removed"].add(player_id)
                state["roster"].pop(player_id, None)
                self.reset(state, event, "Sending-off")
        elif kind == "Pass":
            details = event.get("pass") or {}
            passer, recipient = event.get("player") or {}, details.get("recipient") or {}
            start, end = event.get("location"), details.get("end_location")
            if (
                details.get("outcome")
                or passer.get("id") is None
                or recipient.get("id") is None
                or passer["id"] == recipient["id"]
                or not valid_location(start)
                or not valid_location(end)
                or passer["id"] in state["removed"]
                or recipient["id"] in state["removed"]
            ):
                return
            for player, location in [(passer, start), (recipient, end)]:
                identity = state["roster"].get(player["id"], player)
                node = state["players"].setdefault(
                    player["id"],
                    {
                        "id": player["id"],
                        "name": identity.get("name", "Player"),
                        "jersey_number": identity.get("jersey_number"),
                        "x": 0.0,
                        "y": 0.0,
                        "involvements": 0,
                    },
                )
                node["x"] += location[0]
                node["y"] += location[1]
                node["involvements"] += 1
            key = tuple(sorted([passer["id"], recipient["id"]]))
            state["links"][key] = state["links"].get(key, 0) + 1
            state["passes"] += 1

    def snapshot(self):
        return {
            str(team): {
                "players": [
                    {
                        **player,
                        "x": player["x"] / player["involvements"],
                        "y": player["y"] / player["involvements"],
                    }
                    for player in state["players"].values()
                ],
                "links": [
                    {"source": source, "target": target, "passes": count}
                    for (source, target), count in state["links"].items()
                ],
                "passes": state["passes"],
                "since": state["since"],
                "reason": state["reason"],
            }
            for team, state in self.teams.items()
        }
