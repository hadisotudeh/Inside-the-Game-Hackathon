"""Reproducible synthetic demo build: .venv/bin/python -m tools.demo.server."""

from pathlib import Path

import uvicorn
from fastapi.responses import HTMLResponse

from app.main import create_app
from app.synthetic import SyntheticSource


class DemoSource(SyntheticSource):
    async def matches(self):
        matches = await super().matches()
        matches[0]["match_date"] = "2026-10-21"
        return matches

    async def events(self, match_id):
        events = await super().events(match_id)
        possession = 0
        previous = None
        for i, event in enumerate(events):
            team = event["team"]
            if team["id"] != previous:
                possession += 1
            previous = team["id"]
            event.update(possession=possession, possession_team=team)
            if "pass" in event:
                following = events[i + 1] if i + 1 < len(events) else {}
                recipient = following.get("player") if following.get("team") == team else None
                event["pass"]["recipient"] = recipient or {
                    "id": team["id"] * 100 + 9,
                    "name": f"{team['name'].split()[0]} 10",
                }
        return events


app = create_app()
app.state.source = DemoSource()
# Keep the ordinary application untouched. This explicit demo build uses the same
# UI, analytics, SSE replay and real Agent Framework/Gemini chat endpoint.
app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", "") != "/overlay"]


@app.get("/overlay", include_in_schema=False)
async def demo_overlay():
    html = Path("app/static/overlay.html").read_text()
    html = html.replace('<script src="/static/stadium.js" defer></script>', "")
    html = html.replace("Premier League <span", "Fictional exhibition <span")
    html = html.replace(
        '<span class="broadcast-live-badge">LIVE</span>',
        '<span class="broadcast-live-badge">SYNTHETIC REPLAY · SEED 42</span>',
    )
    html = html.replace(
        '<option value="2" selected>2×</option>',
        '<option value="2">2×</option><option value="60" selected>60× · Demo</option>',
    )
    start, end = html.index("    <footer>"), html.index("</footer>") + len("</footer>")
    html = (
        html[:start]
        + (
            "<footer><span>Fictional teams and events · seed 42 · "
            "heuristic xG, not calibrated · local prototype</span></footer>"
        )
        + html[end:]
    )
    html = html.replace(
        "</head>",
        "<style>.broadcast-live-badge{font-size:11px!important;letter-spacing:.04em!important}.broadcast-brand{gap:18px!important}</style></head>",
    )
    return HTMLResponse(html)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8012)
