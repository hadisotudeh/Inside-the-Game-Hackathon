"""Seeded fictional matches; no historical events or player identities are copied."""

import math
import random


class SyntheticSource:
    async def matches(self) -> list[dict]:
        return [
            {
                "match_id": 1,
                "match_date": "Fictional exhibition",
                "home_team": {"id": 101, "name": "Northbridge FC"},
                "away_team": {"id": 202, "name": "Southbank United"},
                "source": "synthetic",
                "seed": 42,
            }
        ]

    async def events(self, match_id: int) -> list[dict]:
        rng = random.Random(42)
        teams = (await self.matches())[0]
        events = []
        possession = 0
        owner = teams["home_team"]

        def player(team, number):
            return {
                "id": team["id"] * 100 + number,
                "name": f"{team['name'].split()[0]} {number}",
            }

        def append(period, clock, kind, team, location=None, **details):
            sequence = len(events) + 1
            minute, second = divmod(int(clock), 60)
            events.append(
                {
                    "id": f"synthetic-42-{sequence}",
                    "index": sequence,
                    "period": period,
                    "timestamp": f"00:{minute:02}:{second:02}.000",
                    "minute": minute + (45 if period == 2 else 0),
                    "second": second,
                    "type": {"name": kind},
                    "team": team,
                    "possession": possession,
                    "possession_team": owner,
                    **({"location": location} if location else {}),
                    **details,
                }
            )

        home, away = teams["home_team"], teams["away_team"]
        for team in (home, away):
            append(
                1,
                0,
                "Starting XI",
                team,
                tactics={
                    "lineup": [
                        {"player": player(team, number), "jersey_number": number}
                        for number in range(1, 12)
                    ]
                },
            )
        for period in (1, 2):
            append(period, 0, "Half Start", home)
            clock = 2
            while clock < 2700:
                # Alternating spells of attacking activity create observable shifts.
                home_bias = 0.7 if (clock // 300 + period) % 2 else 0.3
                team = home if rng.random() < home_bias else away
                opponent = away if team == home else home
                possession += 1
                owner = team
                carrier = player(team, rng.randint(2, 11))
                x, y = rng.uniform(30, 55), rng.uniform(15, 65)
                lost_ball = False
                for _ in range(rng.randint(3, 8)):
                    if clock >= 2690:
                        break
                    end = [
                        round(min(110, x + rng.uniform(3, 15)), 1),
                        round(max(2, min(78, y + rng.uniform(-15, 15))), 1),
                    ]
                    kind = "Carry" if rng.random() < 0.3 else "Pass"
                    recipient = player(
                        team,
                        rng.choice(
                            [
                                number
                                for number in range(2, 12)
                                if team["id"] * 100 + number != carrier["id"]
                            ]
                        ),
                    )
                    failed = kind == "Pass" and rng.random() < 0.12
                    details = {"end_location": end}
                    if kind == "Pass":
                        details["recipient"] = recipient
                        if failed:
                            details["outcome"] = {"name": "Incomplete"}
                    if rng.random() < 0.18:
                        append(
                            period,
                            clock,
                            "Pressure",
                            opponent,
                            [round(120 - x, 1), round(80 - y, 1)],
                            player=player(opponent, rng.randint(2, 11)),
                        )
                    append(
                        period,
                        clock,
                        kind,
                        team,
                        [round(x, 1), round(y, 1)],
                        player=carrier,
                        **{kind.lower(): details},
                    )
                    x, y = end
                    clock += rng.randint(4, 9)
                    if failed:
                        possession += 1
                        owner = opponent
                        append(
                            period,
                            clock,
                            "Ball Recovery",
                            opponent,
                            [round(120 - x, 1), round(80 - y, 1)],
                            player=player(opponent, rng.randint(2, 11)),
                        )
                        lost_ball = True
                        break
                    if kind == "Pass":
                        carrier = recipient
                if not lost_ball and clock < 2690 and x >= 80 and rng.random() < 0.5:
                    # Illustrative distance/angle heuristic, not a calibrated xG model.
                    distance = math.hypot(120 - x, 40 - y)
                    xg = round(max(0.02, min(0.65, 0.6 * math.exp(-distance / 15))), 3)
                    roll = rng.random()
                    outcome = "Goal" if roll < xg else rng.choice(["Saved", "Off T", "Blocked"])
                    append(
                        period,
                        clock,
                        "Shot",
                        team,
                        [x, y],
                        player=carrier,
                        shot={
                            "statsbomb_xg": xg,
                            "outcome": {"name": outcome},
                            "body_part": {"name": "Right Foot"},
                            "type": {"name": "Open Play"},
                        },
                    )
                    clock += 5
                clock += rng.randint(4, 12)
            append(period, 2700, "Half End", home)
        return events
