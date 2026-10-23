# ruff: noqa: E501
"""Record the deployed Azure overlay and a real Azure model answer; never replace data."""

import asyncio
import json
import os
import time
from pathlib import Path

from playwright.async_api import async_playwright
from title_card import architecture_card, microsoft_card, opening_card

LIVE_URL = "https://touchline-inside-the-game.azurewebsites.net"

OUT = Path(os.environ.get("TOUCHLINE_DEMO_OUT", ".demo-production"))
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
    narration = json.loads((OUT / "narration-report.json").read_text())
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
        await page.goto(LIVE_URL, timeout=90000)
        await page.wait_for_function('!document.getElementById("play").disabled', timeout=90000)
        await page.locator("#match").select_option("3754217")
        await page.add_style_tag(content=CSS)
        await page.evaluate("""() => {
            const speed=document.getElementById('speed');
            speed.value='15';
            document.querySelector('.broadcast-controls').open=false;
            document.querySelector('.broadcast-live-badge').textContent='HISTORICAL REPLAY · 15×';
            document.body.insertAdjacentHTML('beforeend',`<div id="editorial">TOUCHLINE / MATCH STATS AND AI</div><div id="case-study"><span>CHELSEA v ARSENAL · 2015/16 CASE STUDY</span><img src="/static/assets/statsbomb.png" alt="StatsBomb"></div>`);
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
                const analysis=document.getElementById('analysis');
                for(const property of ['transform','left','top','transition'])analysis.style.removeProperty(property);
                analysis.className=name;
                if(name==='camera-momentum'){
                    analysis.style.setProperty('transition','none','important');
                    analysis.style.setProperty('transform','translateX(-50%) scale(1.45)','important');
                    const bounds=document.querySelector(focus).getBoundingClientRect();
                    analysis.style.setProperty('left',`${window.innerWidth/2+(window.innerWidth/2-(bounds.left+bounds.width/2))}px`,'important');
                    analysis.style.setProperty('top',`${40+(480-(bounds.top+bounds.height/2))}px`,'important');
                }
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

        await chapter(1)
        # This editorial launcher records an actual navigation to the public URL.
        await page.evaluate(
            """url => {
            document.body.insertAdjacentHTML('beforeend', `<section id="live-launch" style="position:fixed;inset:0;z-index:9998;background:#fff;padding:150px 128px;font:32px Arial;color:#17212b;box-sizing:border-box"><p style="color:#126347;letter-spacing:3px">ALREADY HOSTED ON AZURE</p><h1 style="font-size:78px">Try Touchline yourself.</h1><p>Open this public address. No installation needed.</p><input aria-label="Live demo URL" id="demo-url" style="width:1500px;padding:24px;font:38px Arial;border:2px solid #126347;border-radius:12px"><p><a id="open-live" href="${url}" style="display:inline-block;padding:22px 38px;border-radius:10px;background:#126347;color:#fff;text-decoration:none">Open live demo →</a></p></section>`);
            // Reveal the URL screen atomically, without exposing the app below.
            document.getElementById('title-card').remove();
        }""",
            LIVE_URL,
        )
        await page.locator("#demo-url").press_sequentially(LIVE_URL, delay=35)
        await page.screenshot(path=str(OUT / "live-url.png"))
        async with page.expect_navigation(wait_until="domcontentloaded"):
            await page.locator("#open-live").click()
        await page.wait_for_function('!document.getElementById("play").disabled', timeout=90000)
        await page.locator("#match").select_option("3754217")
        await page.add_style_tag(content=CSS)
        await page.evaluate(
            """url => {
            const speed=document.getElementById('speed');
             speed.value='15';
            document.querySelector('.broadcast-controls').open=false;
            document.querySelector('.broadcast-live-badge').textContent='HISTORICAL REPLAY · 15×';
            document.body.insertAdjacentHTML('beforeend', `<div id="editorial">OPEN THE LIVE AZURE DEMO</div><div id="case-study"><span>LIVE AZURE SITE · HISTORICAL MATCH DATA</span></div><div style="position:fixed;bottom:110px;left:128px;z-index:9002;font:22px Arial;color:#fff;background:#101820;padding:12px 20px;border-radius:8px">${url}</div>`);
        }""",
            LIVE_URL,
        )
        await page.evaluate("start()")
        await camera("", "#eventLocations")
        await chapter(2)
        await camera("", "#eventLocations")
        await chapter(3)
        await camera("", ".top-stats")
        await page.locator(".broadcast-controls").evaluate("el=>el.open=true")
        await page.locator("#speed").focus()
        await at(chapters[3]["start"] + 2)
        await page.locator(".broadcast-controls").evaluate("el=>el.open=false")
        await page.screenshot(path=str(OUT / "streaming.png"))
        await chapter(4)
        await camera("camera-shot", "#shots")
        await at(chapters[4]["start"] + 2)
        markers = page.locator("#shotPitch .shot-marker")
        if await markers.count():
            await markers.first.click(force=True)
        await at(chapters[4]["start"] + 3)
        await page.screenshot(path=str(OUT / "shot-selection.png"))
        await camera("camera-momentum", "#momentumSection")
        await at(chapters[4]["end"] - 3)
        await page.screenshot(path=str(OUT / "momentum-closeup.png"))
        await camera("camera-network", ".passing-card")
        await page.locator("#passingTeam").select_option("away")
        await chapter(5)
        await camera("camera-chat", "#commentary")
        await page.select_option("#intelligenceMode", "timeline")
        await page.wait_for_selector(".ai-note", timeout=30000)
        await page.screenshot(path=str(OUT / "ai-answer.png"))
        await at(chapters[5]["start"] + 8)
        await page.locator("#aiTimeline").evaluate("el=>el.scrollTop=0")
        await chapter(6)
        await page.select_option("#intelligenceMode", "ask")
        await page.locator("[data-question]").first.click(force=True)
        await at(chapters[6]["end"] - 2)
        await page.screenshot(path=str(OUT / "chat-answer.png"))
        await camera()
        await page.screenshot(path=str(OUT / "overlay.png"))
        await chapter(7)
        await page.select_option("#intelligenceMode", "ask")
        await page.evaluate(
            "html => document.body.insertAdjacentHTML('beforeend', html)",
            opening_card(historical=True),
        )
        await page.locator("#title-card").evaluate(
            "(el, html) => {el.innerHTML = html; el.style.opacity = '1';}",
            architecture_card(),
        )
        # Follow the five spoken sentences with matching diagram highlights.
        voice = narration["chapters"][7]
        sentences = chapters[7]["text"].split(". ")
        unit = (voice["speech_end"] - voice["speech_start"]) / sum(map(len, sentences))
        cue = chapters[7]["start"] + voice["speech_start"]
        stages = [
            ["arch-events", "arch-server"],
            ["arch-server", "arch-browser"],
            ["arch-ai"],
            ["arch-model"],
            ["arch-checks", "arch-browser"],
        ]
        for sentence, stage in zip(sentences, stages, strict=True):
            await at(cue)
            await page.evaluate(
                """ids=>{
                document.querySelectorAll('#title-card [id^="arch-"]').forEach(el=>{
                    el.style.outline='';el.style.outlineOffset='';
                });
                ids.forEach(id=>{
                    const el=document.getElementById(id);
                    el.style.outline='4px solid #126347';el.style.outlineOffset='6px';
                });
            }""",
                stage,
            )
            cue += len(sentence) * unit
        await at(chapters[7]["end"] - 0.5)
        await page.screenshot(path=str(OUT / "architecture-slide.png"))
        await chapter(8)
        await page.locator("#title-card").evaluate(
            "(el, html) => {el.innerHTML = html; el.style.opacity = '1';}", microsoft_card()
        )
        await at(total - 1)
        await page.screenshot(path=str(OUT / "closing-slide.png"))
        await at(total)
        (OUT / "recording-report.json").write_text(
            json.dumps(
                {
                    "url": LIVE_URL,
                    "live_url_navigation": True,
                    "intelligence_modes": ["ask", "timeline"],
                    "default_intelligence_mode": "timeline",
                    "momentum_metric": await page.evaluate("history[history.length-1]?.metric"),
                    "timeline_notes": await page.locator(".ai-note").count(),
                    "match_id": 3754217,
                    "match": "Chelsea v Arsenal, 19 September 2015",
                    "source": "StatsBomb historical open data",
                    "speed": 15,
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
        print("Recorded live Azure overlay:", path, flush=True)
        print(
            "Page errors:", errors, "Chat statuses:", [x["status"] for x in responses], flush=True
        )


asyncio.run(main())
