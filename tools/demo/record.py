# ruff: noqa: E501
"""Record genuine browser interactions, with editorial titles and camera moves."""

import asyncio
import json
import time
from pathlib import Path

from title_card import opening_card

from playwright.async_api import async_playwright

OUT = Path("artifacts/demo")
CSS = Path("tools/demo/editorial.css").read_text()


async def main():
    story = json.loads(Path("tools/demo/story.json").read_text())
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome-stable",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(OUT / "raw"),
            record_video_size={"width": 1920, "height": 1080},
            device_scale_factor=1,
        )
        page = await context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        responses = []

        async def log_chat(response):
            if response.url.endswith("/chat"):
                try:
                    responses.append({"status": response.status, "body": await response.json()})
                except Exception:
                    pass

        page.on("response", log_chat)
        await page.goto("http://127.0.0.1:8012/overlay")
        await page.wait_for_function('!document.getElementById("play").disabled')
        await page.add_style_tag(content=CSS)
        await page.evaluate("""() => {
          document.querySelector('.broadcast-controls').open=false;
          document.body.insertAdjacentHTML('beforeend',`<div id="editorial">TOUCHLINE / FOOTBALL INTELLIGENCE</div><div id="cut-count">LOCAL PROTOTYPE</div>`);
        }""")
        await page.evaluate("html => document.body.insertAdjacentHTML('beforeend', html)", opening_card(historical=False))
        # Video includes setup frames, measured below and removed during export.
        video = page.video
        setup = await page.evaluate("performance.now()")
        started = time.monotonic()

        async def at(seconds):
            await asyncio.sleep(max(0, started + seconds - time.monotonic()))

        async def camera(name="", focus=""):
            await page.evaluate(
                """([name,focus])=>{document.getElementById('analysis').className=name;document.querySelectorAll('.demo-focus').forEach(x=>x.classList.remove('demo-focus'));if(focus)document.querySelector(focus).classList.add('demo-focus')}""",
                [name, focus],
            )

        async def chapter(i):
            await page.locator("#editorial").evaluate(
                "(el,text)=>el.textContent=text", story[i]["label"]
            )
            await page.locator("#cut-count").evaluate(
                "(el,text)=>el.textContent=text", f"{i + 1:02} / 08"
            )

        await at(8)
        await page.locator("#title-card").evaluate("el=>el.style.opacity='0'")
        await page.evaluate("start()")
        await at(10)
        await chapter(1)
        await at(26)
        await chapter(2)
        await camera("camera-shot", "#shots")
        await at(29)
        markers = page.locator("#shotPitch .shot-marker")
        if await markers.count():
            await markers.first.click(force=True)
        await at(34)
        # Return to the full overlay so the progression chart can be seen.
        await camera("", "#momentumSection")
        await at(43)
        await chapter(3)
        await camera("camera-network", ".passing-card")
        await at(48)
        await page.locator("#passingTeam").select_option("away")
        await at(53)
        await page.locator("#passingTeam").select_option("home")
        await at(57)
        await chapter(4)
        await camera("camera-chat", "#commentary")
        await page.locator("[data-question]").first.click(force=True)
        await at(69)
        await page.screenshot(path=str(OUT / "ai-answer.png"))
        await at(75)
        await at(78)
        await chapter(5)
        await at(88)
        await page.screenshot(path=str(OUT / "evidence.png"))
        await camera("", "#commentary")
        await at(96)
        await chapter(6)
        await camera()
        await at(104)
        await page.screenshot(path=str(OUT / "overlay.png"))
        await at(108)
        await chapter(7)
        await page.locator("#title-card").evaluate(
            """el=>{el.innerHTML='<div class="eyebrow">TOUCHLINE / FOOTBALL INTELLIGENCE</div><h1>Every event.<br><span>A story worth seeing.</span></h1><div class="rule"></div><p>Reproducible events. Explainable metrics.<br>Questions grounded in the match so far.</p><div class="small">MICROSOFT AGENT FRAMEWORK + GEMINI · LOCAL PROTOTYPE</div>';el.style.opacity='1'}"""
        )
        await at(118)
        Path(OUT / "recording-report.json").write_text(
            json.dumps(
                {
                    "setup_milliseconds": setup,
                    "page_errors": errors,
                    "chat_responses": responses,
                    "duration_seconds": 118,
                },
                indent=2,
            )
        )
        await context.close()
        path = await video.path()
        Path(OUT / "raw-path.txt").write_text(str(path))
        await browser.close()
        print(
            "Recording:",
            path,
            "; page errors:",
            errors,
            "; chat statuses:",
            [x["status"] for x in responses],
            flush=True,
        )


asyncio.run(main())
