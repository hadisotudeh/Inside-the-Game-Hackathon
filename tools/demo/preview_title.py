"""Render a standalone title-card preview at the demo's native resolution."""

import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright
from title_card import opening_card


async def main():
    out = Path(os.environ.get("TOUCHLINE_DEMO_OUT", "artifacts/demo-real"))
    html = (
        "<html><head><style>"
        + Path("tools/demo/editorial.css").read_text()
        + "</style></head><body>"
        + opening_card()
        + "</body></html>"
    )
    (out / "opening-slide.html").write_text(html)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome-stable", args=["--no-sandbox"]
        )
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.set_content(html)
        await page.evaluate("document.fonts.ready")
        assert await page.locator("#title-card img").evaluate_all(
            "(imgs)=>imgs.every(i=>i.complete&&i.naturalWidth>0)"
        )
        await page.screenshot(path=str(out / "opening-slide.png"))
        await browser.close()


asyncio.run(main())
