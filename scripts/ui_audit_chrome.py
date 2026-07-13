# -*- coding: utf-8 -*-
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\create\综漫")
UI = ROOT / "src/shengtang/ui"
OUT = ROOT / "tmp/ui-audit"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STATUS = (UI / "status/index.html").as_uri() + "?demo=1"
COVER = (UI / "cover/index.html").as_uri()
VIEWPORTS = [("desktop", 1280, 800), ("tablet", 768, 1024), ("mobile", 390, 844)]

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        page = browser.new_page()
        for name, w, h in VIEWPORTS:
            page.set_viewport_size({"width": w, "height": h})

            page.goto(STATUS, wait_until="domcontentloaded")
            page.wait_for_timeout(1200)
            page.locator(".stat").first.click()
            page.wait_for_timeout(800)
            page.screenshot(path=str(OUT / f"status-{name}.png"), full_page=True)

            page.goto(COVER, wait_until="domcontentloaded")
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUT / f"cover-p1-{name}.png"), full_page=True)

            page.click("#btnEnter")
            page.wait_for_timeout(350)
            page.click("#btnToMeet")
            page.wait_for_timeout(500)
            if page.locator(".char-card").count() > 0:
                page.locator(".char-card").first.click()
                page.wait_for_timeout(450)
            page.screenshot(path=str(OUT / f"cover-p3-{name}.png"), full_page=True)
        browser.close()
    print("ok")

if __name__ == "__main__":
    main()
