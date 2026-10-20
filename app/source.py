"""Fetch historical fixtures on demand without bundling or persisting data."""

import httpx

BASE_URL = "https://raw.githubusercontent.com/hudl/open-data/master/data/"


class StatsBombSource:
    async def _get(self, path: str) -> list[dict]:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(BASE_URL + path)
            response.raise_for_status()
            return response.json()

    async def matches(self) -> list[dict]:
        matches = await self._get("matches/2/27.json")
        # Do not expose final scores or match reports before a replay starts.
        return [
            {
                "match_id": m["match_id"],
                "match_date": m["match_date"],
                "home_team": {
                    "id": m["home_team"]["home_team_id"],
                    "name": m["home_team"]["home_team_name"],
                },
                "away_team": {
                    "id": m["away_team"]["away_team_id"],
                    "name": m["away_team"]["away_team_name"],
                },
            }
            for m in matches
        ]

    async def events(self, match_id: int) -> list[dict]:
        events = await self._get(f"events/{match_id}.json")
        return sorted(events, key=lambda event: event["index"])
