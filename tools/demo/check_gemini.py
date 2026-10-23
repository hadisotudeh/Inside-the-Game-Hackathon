"""Check one real Gemini answer using the running replay UI."""

import asyncio
import json
import os
from pathlib import Path

from playwright.async_api import async_playwright

OUT = Path(os.environ.get("TOUCHLINE_DEMO_OUT", ".demo-production"))


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome-stable", args=["--no-sandbox"]
        )
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.goto("http://127.0.0.1:8000/overlay", timeout=90000)
        await page.wait_for_function('!document.getElementById("play").disabled', timeout=90000)
        await page.locator("#match").select_option("3754217")
        await page.evaluate(
            "document.getElementById('speed').add(new Option('60x','60'));"
            "document.getElementById('speed').value='60';start()"
        )
        await page.wait_for_timeout(6000)
        async with page.expect_response(
            lambda r: r.url.endswith("/chat"), timeout=45000
        ) as pending:
            await page.locator("[data-question]").first.click(force=True)
        response = await pending.value
        result = {"status": response.status, "body": await response.json()}
        (OUT / "gemini-check.json").write_text(json.dumps(result, indent=2))
        await page.screenshot(path=str(OUT / "gemini-check.png"))
        print(json.dumps(result))
        await browser.close()


asyncio.run(main())
