# ruff: noqa: E501
"""Record the user's existing historical overlay on port 8000; never replace data."""

import asyncio
import json
import os
import time
from pathlib import Path

from playwright.async_api import async_playwright
from title_card import microsoft_card, opening_card

OUT = Path(os.environ.get("TOUCHLINE_DEMO_OUT", "artifacts/demo"))
CSS = (
    Path("tools/demo/editorial.css").read_text()
    + """
#case-study{position:fixed;right:115px;top:9px;z-index:9001;display:flex;gap:12px;align-items:center;color:#d4dde1;background:#101820;padding:5px 10px;border-radius:5px;font:13px Arial}
#case-study img{width:95px;height:auto;filter:brightness(0) invert(1)}
#editorial{font-size:14px;letter-spacing:1px;max-width:720px}
#cut-count{display:none}
.camera-chat #commentary{height:475px!important;min-height:475px!important;transform:translateY(-110px)}
.camera-chat #commentary .chat-reply{font-size:16px;line-height:1.45}
.camera-chat #commentary .chat-suggestions{display:flex}
.camera-chat #commentary:has(.chat-reply p:nth-child(2)) .chat-suggestions{display:none}
"""
)


async def main():
    timeline = json.loads((OUT / "timeline.json").read_text())
    chapters = timeline["chapters"]
    total = timeline["duration"]
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome-stable",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            record_video_dir=str(OUT / "raw"),
            record_video_size={"width": 1920, "height": 1080},
        )
        page = await context.new_page()
        errors, responses = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))

        async def log_response(response):
            if response.url.endswith("/chat"):
                try:
                    responses.append({"status": response.status, "body": await response.json()})
                except Exception:
                    pass

        page.on("response", log_response)
        await page.goto("http://127.0.0.1:8000/overlay", timeout=90000)
        await page.wait_for_function('!document.getElementById("play").disabled', timeout=90000)
        await page.locator("#match").select_option("3754217")
        await page.add_style_tag(content=CSS)
        await page.evaluate("""() => {
            const speed=document.getElementById('speed');
            speed.add(new Option('60× · Accelerated case study','60'));
            speed.value='60';
            document.querySelector('.broadcast-controls').open=false;
            document.querySelector('.broadcast-live-badge').textContent='HISTORICAL REPLAY · 60×';
            document.body.insertAdjacentHTML('beforeend',`<div id="editorial">TOUCHLINE / THE STORY BEHIND THE SCORE</div><div id="case-study"><span>CHELSEA v ARSENAL · 2015/16 CASE STUDY</span><img src="/static/assets/statsbomb.png" alt="StatsBomb"></div>`);
        }""")
        await page.evaluate(
            "html => document.body.insertAdjacentHTML('beforeend', html)",
            opening_card(historical=True),
        )
        video = page.video
        started = time.monotonic()
        clock_samples = []

        async def at(seconds):
            await asyncio.sleep(max(0, started + seconds - time.monotonic()))

        async def camera(name="", focus=""):
            await page.evaluate(
                """([name,focus])=>{
                document.getElementById('analysis').className=name;
                document.querySelectorAll('.demo-focus').forEach(x=>x.classList.remove('demo-focus'));
                if(focus)document.querySelector(focus).classList.add('demo-focus');
            }""",
                [name, focus],
            )

        async def chapter(i):
            await at(chapters[i]["start"])
            await page.locator("#editorial").evaluate(
                "(el,text)=>el.textContent=text", chapters[i]["label"]
            )
            clock_samples.append({"chapter": i, "clock": await page.locator("#clock").inner_text()})

        await at(max(1, chapters[0]["end"] - 0.8))
        await page.locator("#title-card").evaluate("el=>el.style.opacity='0'")
        await page.evaluate("start()")
        await chapter(1)
        await camera("", "#eventLocations")
        await chapter(2)
        await camera("", "#eventLocations")
        await chapter(3)
        await camera("", ".top-stats")
        await page.screenshot(path=str(OUT / "streaming.png"))
        await chapter(4)
        await camera("camera-shot", "#shots")
        await at(chapters[4]["start"] + 2)
        markers = page.locator("#shotPitch .shot-marker")
        if await markers.count():
            await markers.first.click(force=True)
        await at(chapters[4]["start"] + 5)
        await page.screenshot(path=str(OUT / "shot-selection.png"))
        await camera("", "#momentumSection")
        await at(chapters[4]["start"] + 8)
        await camera("camera-network", ".passing-card")
        await page.locator("#passingTeam").select_option("away")
        await chapter(5)
        await camera("camera-chat", "#commentary")
        await page.locator("[data-question]").first.click(force=True)
        await chapter(6)
        await page.screenshot(path=str(OUT / "ai-answer.png"))
        await at(chapters[6]["start"] + 4)
        await page.locator("#chatReply").evaluate("el=>el.scrollTop=el.scrollHeight")
        await at(chapters[6]["end"] - 1)
        await camera()
        await page.screenshot(path=str(OUT / "overlay.png"))
        await chapter(7)
        await page.locator("#title-card").evaluate("""el=>{
            el.innerHTML='<div class="eyebrow">TOUCHLINE / FOOTBALL INTELLIGENCE</div><h1>Every event.<br><span>A story worth seeing.</span></h1><div class="rule"></div><p>Designed for live TV and streaming.<br>Demonstrated with historical Premier League event data.</p><div class="small">MICROSOFT AGENT FRAMEWORK + GEMINI · LOCAL PROTOTYPE · BROADCAST SYNC PLANNED</div>';
            el.style.opacity='1';
        }""")
        if os.environ.get("TOUCHLINE_DEMO_MICROSOFT") == "1":
            await page.locator("#title-card").evaluate(
                "(el, html) => {el.innerHTML = html; el.style.opacity = '1';}", microsoft_card()
            )
        await at(total - 1)
        await page.screenshot(path=str(OUT / "closing-slide.png"))
        await at(total)
        (OUT / "recording-report.json").write_text(
            json.dumps(
                {
                    "url": "http://127.0.0.1:8000/overlay",
                    "match_id": 3754217,
                    "match": "Chelsea v Arsenal, 19 September 2015",
                    "source": "StatsBomb historical open data",
                    "speed": 60,
                    "page_errors": errors,
                    "chat_responses": responses,
                    "clock_samples": clock_samples,
                    "duration_seconds": total,
                },
                indent=2,
            )
        )
        await context.close()
        path = await video.path()
        (OUT / "raw-path.txt").write_text(str(path))
        await browser.close()
        print("Recorded actual port-8000 overlay:", path, flush=True)
        print(
            "Page errors:", errors, "Chat statuses:", [x["status"] for x in responses], flush=True
        )


asyncio.run(main())
