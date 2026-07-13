# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp" / "ui-audit"
COVER = (ROOT / "src/shengtang/ui/cover/index.html").resolve().as_uri()
STATUS = (ROOT / "src/shengtang/ui/status/index.html").resolve().as_uri()

INIT = """
window.getAllVariables = () => ({stat_data:{
  世界:{相遇方式:"求净上门",场景:"圣言堂·告解室",教会名:"圣言堂",回合:3},
  初遇:{姓名:"芙莉莲",作品:"葬送的芙莉莲",污秽类型:"讨伐恶魔时沾上的魔力残渣",
        污秽度:58,信任:46,好感度:32,堕落值:18,依存度:12,
        仪式阶段:"仪式中",与user关系:"半信半疑",当前心态:"觉得麻烦，但魔力紊乱让她不得不配合。"}
}});
"""


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge")

        page = await browser.new_page(viewport={"width": 768, "height": 1024})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(COVER, wait_until="load")
        await page.wait_for_timeout(900)
        info = await page.evaluate(
            """() => ({
            modes: typeof MEETING_MODES!=='undefined' ? MEETING_MODES.length : -1,
            chars: typeof CHARACTERS!=='undefined' ? CHARACTERS.length : -1,
            modeCards: document.querySelectorAll('.mode-card').length,
            charCards: document.querySelectorAll('.char-card').length
        })"""
        )
        print("cover", info)
        print("errors", errors)

        await page.evaluate(
            """() => {
            document.querySelectorAll('.page').forEach((p,i)=>p.classList.toggle('active', i===2));
            const c=document.querySelector('.char-card');
            if (c) c.click();
        }"""
        )
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(OUT / "cover-p3-tablet.png"), full_page=True)

        for name, w, h in [("mobile", 390, 844), ("tablet", 768, 1024), ("desktop", 1280, 900)]:
            sp = await browser.new_page(viewport={"width": w, "height": h})
            await sp.add_init_script(INIT)
            await sp.goto(STATUS, wait_until="load")
            await sp.evaluate(
                """() => {
                document.documentElement.style.background =
                  'radial-gradient(900px 500px at 15% 0%, rgba(158,61,74,.45), transparent 55%), radial-gradient(800px 480px at 90% 10%, rgba(91,124,153,.35), transparent 50%), linear-gradient(180deg,#1a1c28,#090a0d)';
                document.body.style.background = 'transparent';
                document.body.style.minHeight = '100vh';
                document.body.style.padding = '16px';
                if (typeof render === 'function') render();
            }"""
            )
            await sp.wait_for_timeout(500)
            await sp.evaluate(
                """() => { const s=document.querySelector('.stat'); if (s) s.click(); }"""
            )
            await sp.wait_for_timeout(500)
            st = await sp.evaluate(
                """() => ({
                name: document.getElementById('name')?.textContent,
                stats: document.querySelectorAll('.stat').length,
                blur: getComputedStyle(document.querySelector('.wrap')).backdropFilter
            })"""
            )
            print("status", name, st)
            await sp.screenshot(path=str(OUT / f"status-{name}.png"), full_page=True)
            await sp.close()

            cp = await browser.new_page(viewport={"width": w, "height": h})
            await cp.goto(COVER, wait_until="load")
            await cp.wait_for_timeout(700)
            await cp.screenshot(path=str(OUT / f"cover-p1-{name}.png"), full_page=True)
            await cp.evaluate(
                """() => document.querySelectorAll('.page').forEach((p,i)=>p.classList.toggle('active', i===2))"""
            )
            await cp.wait_for_timeout(400)
            await cp.evaluate("""() => { const c=document.querySelector('.char-card'); if(c) c.click(); }""")
            await cp.wait_for_timeout(350)
            await cp.screenshot(path=str(OUT / f"cover-p3-{name}.png"), full_page=True)
            await cp.close()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
