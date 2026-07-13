# -*- coding: utf-8 -*-
"""Screenshot cover + status at desktop/tablet/mobile for visual QA."""
from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "src/shengtang/ui"
OUT = ROOT / "tmp/ui-audit"
PREVIEW = (UI / "preview.html").as_uri()

VIEWPORTS = [
    ("desktop", 1280, 800),
    ("tablet", 768, 1024),
    ("mobile", 390, 844),
]


async def shot_status(page, name: str, w: int, h: int):
    await page.set_viewport_size({"width": w, "height": h})
    await page.goto(PREVIEW, wait_until="networkidle")
    await page.click('button[data-pane="status"]')
    await page.wait_for_timeout(900)
    # open one impact panel
    frame = page.frame_locator("#statusFrame")
    await frame.locator(".stat").first.click()
    await page.wait_for_timeout(600)
    await page.screenshot(path=str(OUT / f"status-{name}.png"), full_page=True)


async def shot_cover(page, name: str, w: int, h: int, page_n: int):
    await page.set_viewport_size({"width": w, "height": h})
    cover = (UI / "cover/index.html").as_uri()
    await page.goto(cover, wait_until="networkidle")
    await page.wait_for_timeout(500)
    if page_n >= 2:
        await page.click("#btnEnter")
        await page.wait_for_timeout(450)
    if page_n >= 3:
        await page.click("#btnToMeet")
        await page.wait_for_timeout(450)
        # select first char if visible
        cards = page.locator(".char-card")
        if await cards.count():
            await cards.first.click()
            await page.wait_for_timeout(350)
    await page.screenshot(path=str(OUT / f"cover-p{page_n}-{name}.png"), full_page=True)


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        for name, w, h in VIEWPORTS:
            await shot_status(page, name, w, h)
            await shot_cover(page, name, w, h, 1)
            await shot_cover(page, name, w, h, 3)
        await browser.close()
    print("wrote screenshots to", OUT)
    for f in sorted(OUT.glob("*.png")):
        print("-", f.name, f.stat().st_size)


if __name__ == "__main__":
    asyncio.run(main())
