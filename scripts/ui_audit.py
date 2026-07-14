# -*- coding: utf-8 -*-
"""Multi-viewport UI audit screenshots via Playwright (Edge)."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp" / "ui-audit" / f"run-{os.getpid()}"
COVER = (ROOT / "src/shengtang/ui/cover/index.html").as_uri()
STATUS = (ROOT / "src/shengtang/ui/status/index.html").as_uri()

VIEWPORTS = [
    ("mobile", 390, 844),
    ("tablet", 768, 1024),
    ("desktop", 1280, 900),
]

SAMPLE_JS = r"""
const auditVariables = {
    stat_data: {
      世界: {
        相遇方式: "求净上门",
        场景: "圣言堂·告解室",
        教会名: "圣言堂",
        回合: 3,
        出场角色: ["芙莉莲", "牧濑红莉栖", "雪之下雪乃", "C.C."]
      },
      角色: {
        芙莉莲: {
          作品: "葬送的芙莉莲", 污秽类型: "魔力残渣", 污秽度: 58,
          信任: 46, 好感度: 32, 堕落值: 18, 依存度: 12,
          仪式阶段: "仪式中", 与user关系: "半信半疑",
          当前心态: "觉得麻烦，但仍在观察净化效果。",
          当前目标: "压下魔力紊乱后继续旅行",
          对user判断: "能力可能有效，动机仍待验证",
          当前边界: "只接受已说明的基础检查"
        },
        牧濑红莉栖: {
          作品: "命运石之门", 污秽类型: "认知回响", 污秽度: 34,
          信任: 28, 好感度: 18, 堕落值: 8, 依存度: 4,
          仪式阶段: "检查", 与user关系: "观察",
          当前心态: "正在分析这里的异常机制。",
          当前目标: "验证净化是否可重复",
          对user判断: "言行尚可，证据不足",
          当前边界: "拒绝缺乏解释的接触"
        },
        雪之下雪乃: {
          作品: "我的青春恋爱物语果然有问题", 污秽类型: "情绪残响", 污秽度: 26,
          信任: 20, 好感度: 12, 堕落值: 5, 依存度: 2,
          仪式阶段: "初见", 与user关系: "戒备",
          当前心态: "不喜欢被当成需要拯救的人。",
          当前目标: "弄清被带到此处的原因",
          对user判断: "态度礼貌，但没有可信依据",
          当前边界: "保持公开距离"
        },
        "C.C.": {
          作品: "Code Geass", 污秽类型: "契约残响", 污秽度: 41,
          信任: 17, 好感度: 9, 堕落值: 6, 依存度: 1,
          仪式阶段: "观察", 与user关系: "陌路",
          当前心态: "正在确认契约是否受到干扰。",
          当前目标: "厘清异常来源",
          对user判断: "尚无足够证据",
          当前边界: "拒绝未经说明的精神干预"
        }
      }
    }
};
window.getCurrentMessageId = () => 7;
window.Mvu = {
  getMvuData: option => option && option.message_id === 7 ? auditVariables : {},
  events: { VARIABLE_UPDATE_ENDED: "mock_variable_update_ended" }
};
window.waitGlobalInitialized = async () => window.Mvu;
window.waitUntil = async predicate => {
  if (!predicate()) throw new Error("mock message stat_data unavailable");
};
if (typeof populateCharacterData === "function") populateCharacterData();
"""


async def shot_status(context, name: str, w: int, h: int, notes: list[str]) -> None:
    page = await context.new_page()
    await page.set_viewport_size({"width": w, "height": h})
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    await page.add_init_script(SAMPLE_JS)
    await page.goto(STATUS, wait_until="load")
    await page.wait_for_timeout(900)
    role = page.locator(".role-chip").nth(3)
    if await role.count():
        await role.click()
    await page.wait_for_timeout(500)
    selected_name = (await page.locator("#name").inner_text()).strip()
    role_count = (await page.locator("#roleCount").inner_text()).strip()
    shell_visible = await page.locator("#stage").is_visible()
    if selected_name != "C.C." or role_count != "4 人" or not shell_visible:
        raise AssertionError(
            f"status-{name}: role switch failed "
            f"(name={selected_name!r}, count={role_count!r}, visible={shell_visible})"
        )
    path = OUT / f"status-{name}.png"
    await page.screenshot(path=str(path), full_page=True)
    overflow = await page.evaluate(
        "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"
    )
    if overflow or errors:
        raise AssertionError(
            f"status-{name}: overflowX={overflow}, pageErrors={errors}"
        )
    notes.append(
        f"{path.name} overflowX={overflow} pageErrors={len(errors)} "
        f"selected={selected_name} roleCount={role_count}"
    )
    notes.extend(f"  ERROR {error}" for error in errors)
    await page.close()


async def shot_cover(context, name: str, w: int, h: int, notes: list[str]) -> None:
    page = await context.new_page()
    await page.set_viewport_size({"width": w, "height": h})
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
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
    detail_visible = await page.locator("#charDetail").is_visible()
    if overflow or errors or not detail_visible:
        raise AssertionError(
            f"cover-{name}: overflowX={overflow}, pageErrors={errors}, "
            f"detailVisible={detail_visible}"
        )
    notes.append(
        f"cover-p3-{name}.png overflowX={overflow} pageErrors={len(errors)} "
        f"detailVisible={detail_visible}"
    )
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
