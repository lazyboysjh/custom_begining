# -*- coding: utf-8 -*-
"""Multi-viewport UI audit screenshots via Playwright (Edge)."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp" / "ui-audit" / f"run-{os.getpid()}"
UI_BASE_URL = os.environ.get("ST_UI_BASE_URL", "").rstrip("/")
COVER = f"{UI_BASE_URL}/cover/index.html" if UI_BASE_URL else (ROOT / "src/shengtang/ui/cover/index.html").as_uri()
STATUS_QUERY = os.environ.get("ST_STATUS_QUERY", "")
STATUS_BASE = f"{UI_BASE_URL}/status/index.html" if UI_BASE_URL else (ROOT / "src/shengtang/ui/status/index.html").as_uri()
STATUS = f"{STATUS_BASE}{STATUS_QUERY}"

VIEWPORTS = [
    ("wide-short", 960, 460),
    ("compact", 320, 520),
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
        出场角色: ["芙莉莲", "牧濑红莉栖", "雪之下雪乃", "C.C.", "2B", "雷姆", "赫萝", "远坂凛"]
      },
      角色: {
        芙莉莲: {
          污秽度: 58, 信任: 12, 好感度: 8, 堕落值: 4, 依存度: 1, 与user关系: "试探合作",
          外貌: "银发垂落肩后，白色旅装沾着细小尘屑。",
          当前状态: "站在烛光外侧，安静分辨空气中的魔力残响。",
          心里想法: "先看看这里的术式，或许能找到有趣的魔法。"
        },
        牧濑红莉栖: {
          污秽度: 34, 信任: 9, 好感度: 3, 堕落值: 1, 依存度: 0, 与user关系: "谨慎观察",
          外貌: "赤色长发披在白大褂外，手里仍攥着记录纸。",
          当前状态: "皱眉检查墙面纹路，试图找出可重复验证的规律。",
          心里想法: "没有数据就不能下结论，先确认这里到底是什么。"
        },
        雪之下雪乃: {
          污秽度: 26, 信任: 4, 好感度: 0, 堕落值: 0, 依存度: 0, 与user关系: "保持距离",
          外貌: "黑色长发整齐垂下，制服衣角没有一丝凌乱。",
          当前状态: "与众人保持半步距离，冷静观察每个人的反应。",
          心里想法: "先听完说明，再判断这是不是另一场拙劣的安排。"
        },
        "C.C.": {
          污秽度: 41, 信任: 2, 好感度: 0, 堕落值: 0, 依存度: 0, 与user关系: "临时合作",
          外貌: "绿色长发搭在黑色拘束服边缘，金色眼睛微微眯起。",
          当前状态: "靠在墙边检查契约感应，暂时没有靠近任何人。",
          心里想法: "这个地方碰得到契约，却未必知道代价是什么。"
        },
        "2B": { 污秽度: 19, 信任: 5, 好感度: 1, 堕落值: 0, 依存度: 0, 与user关系: "任务接触", 外貌: "银发与黑色战斗服。", 当前状态: "正在扫描现场。", 心里想法: "先确认任务目标。" },
        雷姆: { 污秽度: 32, 信任: 6, 好感度: 2, 堕落值: 0, 依存度: 0, 与user关系: "初步信任", 外貌: "蓝发女仆装。", 当前状态: "守在门边。", 心里想法: "还需要继续观察。" },
        赫萝: { 污秽度: 22, 信任: 7, 好感度: 4, 堕落值: 0, 依存度: 0, 与user关系: "同行试探", 外貌: "狼耳与栗色长发。", 当前状态: "听着远处动静。", 心里想法: "这地方倒有些意思。" },
        远坂凛: { 污秽度: 28, 信任: 3, 好感度: 0, 堕落值: 0, 依存度: 0, 与user关系: "术式协作", 外貌: "黑发红衣。", 当前状态: "检查地面术式。", 心里想法: "先别急着下结论。" }
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


async def load_ui(page, url: str) -> None:
    if not UI_BASE_URL:
        await page.goto(url, wait_until="load")
        return

    response = await page.request.get(url)
    if not response.ok:
        raise AssertionError(f"CDN request failed: {url} -> {response.status}")
    await page.set_content(await response.text(), wait_until="load")


async def shot_status(context, name: str, w: int, h: int, notes: list[str]) -> None:
    page = await context.new_page()
    await page.set_viewport_size({"width": w, "height": h})
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    await page.add_init_script(SAMPLE_JS)
    if UI_BASE_URL:
        await page.evaluate(SAMPLE_JS)
    await load_ui(page, STATUS)
    await page.wait_for_timeout(900)
    role = page.locator(".role-chip").nth(3)
    if await role.count():
        await role.click()
    await page.wait_for_timeout(500)
    selected_name = (await page.locator("#name").inner_text()).strip()
    role_count = (await page.locator("#roleCount").inner_text()).strip()
    chip_count = await page.locator(".role-chip").count()
    relationship = (await page.locator("#relationship").inner_text()).strip()
    icon_count = await page.locator(".command-btn .ui-icon").count()
    scenario_audit = await page.evaluate("""() => {
      const originalRandom = Math.random;
      let cursor = 0;
      Math.random = () => ((cursor++ % 8) + .05) / 8;
      const multiStat = readStat();
      const multi = Array.from({ length: 8 }, () => pickAdvanceScenario(multiStat).id);
      const single = structuredClone(multiStat);
      single.世界.出场角色 = ["芙莉莲"];
      cursor = 0;
      const solo = Array.from({ length: 8 }, () => pickAdvanceScenario(single).id);
      Math.random = originalRandom;
      return { multi: [...new Set(multi)], solo: [...new Set(solo)] };
    }""")
    shell_visible = await page.locator("#stage").is_visible()
    visible_details = all([
        await page.locator("#appearance").is_visible(),
        await page.locator("#currentState").is_visible(),
        await page.locator("#innerThought").is_visible(),
    ])
    removed_copy = await page.locator("text=篇章").count() + await page.locator("text=观感").count()
    if (
        selected_name != "C.C."
        or role_count != "8 人"
        or chip_count != 8
        or relationship != "临时合作"
        or icon_count != 2
        or len(scenario_audit["multi"]) != 8
        or "ensemble" in scenario_audit["solo"]
        or not shell_visible
        or not visible_details
        or removed_copy
    ):
        raise AssertionError(
            f"status-{name}: role switch failed "
            f"(name={selected_name!r}, count={role_count!r}, chips={chip_count}, relationship={relationship!r}, visible={shell_visible}, "
            f"icons={icon_count}, scenarios={scenario_audit}, details={visible_details}, removedCopy={removed_copy})"
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
        f"selected={selected_name} roleCount={role_count} relationship={relationship}"
    )
    notes.extend(f"  ERROR {error}" for error in errors)
    await page.close()


async def shot_cover(context, name: str, w: int, h: int, notes: list[str]) -> None:
    page = await context.new_page()
    await page.set_viewport_size({"width": w, "height": h})
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    await load_ui(page, COVER)
    await page.wait_for_timeout(800)
    cover_identity = await page.evaluate("""() => {
      const body = document.querySelector('.page[data-page="1"] .page-body').getBoundingClientRect();
      const hero = document.querySelector('.page[data-page="1"] .hero-glass').getBoundingClientRect();
      return {
        bodyWidth: body.width,
        bodyHeight: body.height,
        heroWidth: hero.width,
        heroHeight: hero.height,
        title: document.querySelector('.page[data-page="1"] h1')?.textContent.trim(),
        credit: document.querySelector('.cover-credit')?.textContent.trim(),
      };
    }""")
    if (
        cover_identity["heroWidth"] < cover_identity["bodyWidth"] * 0.8
        or cover_identity["heroHeight"] < cover_identity["bodyHeight"] * 0.65
        or cover_identity["title"] != "万界圣堂"
        or cover_identity["credit"] != "AUTHOR · AME"
    ):
        raise AssertionError(f"cover-{name}: weak cover identity {cover_identity}")
    await page.screenshot(path=str(OUT / f"cover-p1-{name}.png"), full_page=True)
    notes.append(f"cover-p1-{name}.png")

    # Drive SPA pages via JS to avoid visibility quirks
    await page.evaluate("typeof showPage === 'function' ? showPage(2) : document.querySelectorAll('.page')[1].classList.add('active')")
    await page.evaluate("""() => {
      document.querySelectorAll('.page').forEach((p,i) => p.classList.toggle('active', i===1));
    }""")
    await page.wait_for_timeout(400)
    option_count = await page.locator("#abilityPreset option").count()
    if option_count < 6:
        raise AssertionError(f"cover-{name}: ability pool too small ({option_count})")
    first_summary = await page.locator("#abilityCustom").input_value()
    await page.locator("#abilityPreset").select_option(index=1)
    second_summary = await page.locator("#abilityCustom").input_value()
    if not first_summary or first_summary == second_summary:
        raise AssertionError(f"cover-{name}: preset did not sync editable summary")
    before_random = await page.locator("#abilityPreset").input_value()
    await page.locator("#btnRandomAbility").click()
    after_random = await page.locator("#abilityPreset").input_value()
    if before_random == after_random:
        raise AssertionError(f"cover-{name}: random ability did not change selection")
    await page.locator("#abilityCustom").fill("可输入的审查能力：让一句约定短暂成为现实。")
    if await page.locator("#abilityPreset").input_value() != "custom":
        raise AssertionError(f"cover-{name}: edited ability did not switch to custom")
    custom_ability = await page.evaluate("selectedAbility(false)")
    if custom_ability.get("id") != "custom" or "可输入的审查能力" not in custom_ability.get("summary", ""):
        raise AssertionError(f"cover-{name}: custom ability was not submitted")
    if (await page.locator("#btnStart").inner_text()).strip() != "那就开始吧~":
        raise AssertionError(f"cover-{name}: ambiguous start copy")
    cover_icons = await page.locator("button .ui-icon").count()
    if cover_icons != 5:
        raise AssertionError(f"cover-{name}: expected 5 button icons, got {cover_icons}")
    await page.screenshot(path=str(OUT / f"cover-p2-{name}.png"), full_page=True)
    notes.append(f"cover-p2-{name}.png")

    await page.evaluate("""() => {
      document.querySelectorAll('.page').forEach((p,i) => p.classList.toggle('active', i===2));
      startReveal(sampleOpeningConfig({ randomAbility: false }));
    }""")
    await page.wait_for_timeout(420)
    await page.screenshot(path=str(OUT / f"cover-p3-spinning-{name}.png"), full_page=True)
    notes.append(f"cover-p3-spinning-{name}.png")
    await page.evaluate("stopOpening('ui audit spinning capture')")
    timer_audit = await page.evaluate("""async () => {
      const before = document.querySelectorAll('*').length;
      const config = sampleOpeningConfig({ randomAbility: false });
      for (let index = 0; index < 3; index += 1) {
        const pending = startReveal(config);
        await new Promise(resolve => setTimeout(resolve, 90));
        stopOpening('ui audit cleanup');
        await pending;
      }
      finishReveal(config);
      return {
        before,
        after: document.querySelectorAll('*').length,
        intervalCleared: state.revealTimer === null,
        timeoutCleared: state.revealFinishTimer === null,
        resolveCleared: state.revealResolve === null,
      };
    }""")
    if (
        timer_audit["before"] != timer_audit["after"]
        or not timer_audit["intervalCleared"]
        or not timer_audit["timeoutCleared"]
        or not timer_audit["resolveCleared"]
    ):
        raise AssertionError(f"cover-{name}: reveal lifecycle leak {timer_audit}")
    await page.wait_for_timeout(350)
    progress_visible = await page.evaluate("""() => {
      const progress = document.querySelector('.summon-progress')?.getBoundingClientRect();
      const body = document.querySelector('.page[data-page="4"] .page-body')?.getBoundingClientRect();
      const meter = document.querySelector('.summon-progress .meter')?.getBoundingClientRect();
      return !!progress && !!body && !!meter && progress.top >= body.top - 1 && progress.bottom <= body.bottom + 1 && meter.height > 0;
    }""")
    await page.screenshot(path=str(OUT / f"cover-p3-{name}.png"), full_page=True)
    overflow = await page.evaluate(
        "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"
    )
    reveal_visible = await page.locator("#revealStage").is_visible()
    reveal_name = (await page.locator("#revealName").inner_text()).strip()
    if overflow or errors or not reveal_visible or not reveal_name or not progress_visible:
        raise AssertionError(
            f"cover-{name}: overflowX={overflow}, pageErrors={errors}, "
            f"revealVisible={reveal_visible}, revealName={reveal_name!r}, progressVisible={progress_visible}"
        )
    notes.append(
        f"cover-p3-{name}.png overflowX={overflow} pageErrors={len(errors)} "
        f"revealVisible={reveal_visible} revealName={reveal_name} domStable={timer_audit['before'] == timer_audit['after']}"
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
