# -*- coding: utf-8 -*-
"""Multi-viewport UI audit screenshots via Playwright (Edge)."""
from __future__ import annotations

import asyncio
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp" / "ui-audit"
COVER = (ROOT / "src/shengtang/ui/cover/index.html").as_uri()
STATUS = (ROOT / "src/shengtang/ui/status/index.html").as_uri()

VIEWPORTS = [
    ("mobile", 390, 844),
    ("tablet", 768, 1024),
    ("desktop", 1280, 900),
]

SAMPLE_JS = r"""
window.getAllVariables = function () {
  return {
    stat_data: {
      世界: { 相遇方式: "求净上门", 场景: "圣言堂·告解室", 教会名: "圣言堂", 回合: 3 },
      初遇: {
        姓名: "芙莉莲",
        作品: "葬送的芙莉莲",
        是否自定义: false,
        污秽类型: "讨伐恶魔时沾上的魔力残渣",
        污秽度: 58,
        信任: 46,
        好感度: 32,
        堕落值: 18,
        依存度: 12,
        仪式阶段: "仪式中",
        与user关系: "半信半疑",
        当前心态: "觉得麻烦，但魔力紊乱让她不得不配合。"
      }
    }
  };
};
if (typeof render === "function") render();
"""


async def shot_status(context, name: str, w: int, h: int, notes: list[str]) -> None:
    page = await context.new_page()
    await page.set_viewport_size({"width": w, "height": h})
    html = f"""<!doctype html><html><head><meta charset="utf-8"></head>
    <body style="margin:0;min-height:100vh;padding:20px 12px 40px;background:
      radial-gradient(900px 500px at 15% 0%, rgba(158,61,74,.42), transparent 55%),
      radial-gradient(800px 480px at 90% 10%, rgba(91,124,153,.34), transparent 50%),
      linear-gradient(180deg,#1a1c28,#090a0d);">
      <iframe id="f" src="{STATUS}" style="width:100%;max-width:920px;height:780px;border:0;display:block;margin:0 auto;background:transparent"></iframe>
      <script>
        const f = document.getElementById('f');
        f.addEventListener('load', () => {{
          const s = f.contentDocument.createElement('script');
          s.textContent = {SAMPLE_JS!r};
          f.contentDocument.body.appendChild(s);
          setTimeout(() => {{
            const st = f.contentDocument.querySelector('.stat');
            if (st) st.click();
          }}, 450);
        }});
      </script>
    </body></html>"""
    await page.set_content(html, wait_until="load")
    await page.wait_for_timeout(1400)
    path = OUT / f"status-{name}.png"
    await page.screenshot(path=str(path), full_page=True)
    overflow = await page.evaluate(
        "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"
    )
    notes.append(f"{path.name} overflowX={overflow}")
    await page.close()


async def shot_cover(context, name: str, w: int, h: int, notes: list[str]) -> None:
    page = await context.new_page()
    await page.set_viewport_size({"width": w, "height": h})
    await page.goto(COVER, wait_until="load")
    await page.wait_for_timeout(800)
    await page.screenshot(path=str(OUT / f"cover-p1-{name}.png"), full_page=True)
    notes.append(f"cover-p1-{name}.png")

    # Drive SPA pages via JS to avoid visibility quirks
    await page.evaluate("typeof showPage === 'function' ? showPage(2) : document.querySelectorAll('.page')[1].classList.add('active')")
    await page.evaluate("""() => {
      document.querySelectorAll('.page').forEach((p,i) => p.classList.toggle('active', i===1));
    }""")
    await page.wait_for_timeout(400)
    await page.screenshot(path=str(OUT / f"cover-p2-{name}.png"), full_page=True)
    notes.append(f"cover-p2-{name}.png")

    await page.evaluate("""() => {
      document.querySelectorAll('.page').forEach((p,i) => p.classList.toggle('active', i===2));
      const card = document.querySelector('.char-card');
      if (card) card.click();
    }""")
    await page.wait_for_timeout(500)
    await page.screenshot(path=str(OUT / f"cover-p3-{name}.png"), full_page=True)
    overflow = await page.evaluate(
        "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"
    )
    notes.append(f"cover-p3-{name}.png overflowX={overflow}")
    await page.close()


async def main() -> None:
    from playwright.async_api import async_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    notes: list[str] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge")
        context = await browser.new_context()
        for name, w, h in VIEWPORTS:
            await shot_cover(context, name, w, h, notes)
            await shot_status(context, name, w, h, notes)
        await browser.close()

    report = OUT / "report.txt"
    report.write_text("\n".join(notes), encoding="utf-8")
    print(report.read_text(encoding="utf-8"))
    print(f"\nshots -> {OUT}")


if __name__ == "__main__":
    asyncio.run(main())
