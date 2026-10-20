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
                    **({"location": location} if location else {}),
                    **details,
                }
            )

        home, away = teams["home_team"], teams["away_team"]
        for period in (1, 2):
            append(period, 0, "Half Start", home)
            clock = 2
            while clock < 2700:
                # Alternating spells of attacking activity create observable shifts.
                home_bias = 0.7 if (clock // 300 + period) % 2 else 0.3
                team = home if rng.random() < home_bias else away
                x, y = rng.uniform(30, 55), rng.uniform(15, 65)
                for action in range(rng.randint(3, 8)):
                    if clock >= 2690:
                        break
                    end = [
                        round(min(110, x + rng.uniform(3, 15)), 1),
                        round(max(2, min(78, y + rng.uniform(-15, 15))), 1),
                    ]
                    kind = "Carry" if rng.random() < 0.3 else "Pass"
                    append(
                        period,
                        clock,
                        kind,
                        team,
                        [round(x, 1), round(y, 1)],
                        player={
                            "id": team["id"] * 100 + action,
                            "name": f"{team['name'].split()[0]} {action + 1}",
                        },
                        **{kind.lower(): {"end_location": end}},
                    )
                    x, y = end
                    clock += rng.randint(4, 9)
                if clock < 2690 and x >= 80 and rng.random() < 0.3:
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
                        player={
                            "id": team["id"] * 100 + 9,
                            "name": f"{team['name'].split()[0]} 10",
                        },
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
