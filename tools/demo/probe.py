import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome-stable", args=["--no-sandbox"]
        )
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        try:
            await page.goto(
                "https://innovationstudio.microsoft.com/hackathons/insidethegamedeveloperhackathon",
                timeout=45000,
            )
            await page.wait_for_timeout(5000)
            text = await page.locator("body").inner_text()
            Path("artifacts/demo/event-page.txt").write_text(text)
            print("EVENT PAGE:", text[:14000])
        except Exception as e:
            print("EVENT PAGE ERROR", str(e)[:300])
        await page.goto("http://127.0.0.1:8012/overlay")
        await page.locator("#play").wait_for(state="visible")
        await page.wait_for_function('!document.getElementById("play").disabled')
        await page.locator("#play").click()
        await page.wait_for_timeout(15000)
        await page.locator("[data-question]").first.click()
        await page.wait_for_timeout(15000)
        print(
            "CHAT:",
            await page.locator("#chatReply").inner_text(),
            await page.locator("#chatStatus").inner_text(),
        )
        await page.screenshot(path="artifacts/demo/probe.png")
        await browser.close()


asyncio.run(main())
