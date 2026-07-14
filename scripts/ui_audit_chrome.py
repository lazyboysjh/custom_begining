# -*- coding: utf-8 -*-
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\create\综漫")
UI = ROOT / "src/shengtang/ui"
OUT = ROOT / "tmp/ui-audit"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STATUS = (UI / "status/index.html").as_uri() + "?demo=1"
STATUS_RUNTIME = (UI / "status/index.html").as_uri()
COVER = (UI / "cover/index.html").as_uri()
VIEWPORTS = [("desktop", 1280, 800), ("tablet", 768, 1024), ("mobile", 390, 844)]

def assert_layout(page, label: str, required_selector: str):
    result = page.evaluate(
        """(selector) => {
          const el = document.querySelector(selector);
          const root = document.documentElement;
          const body = document.body;
          const box = el && el.getBoundingClientRect();
          const offenders = [...document.querySelectorAll("body *")]
            .map(node => {
              const rect = node.getBoundingClientRect();
              return {tag: node.tagName, id: node.id, cls: node.className, left: rect.left, right: rect.right, width: rect.width};
            })
            .filter(item => item.left < -1 || item.right > innerWidth + 1)
            .slice(0, 8);
          return {
            selector,
            found: !!el,
            horizontalOverflow: Math.max(root.scrollWidth, body.scrollWidth) - root.clientWidth,
            elementWidth: box ? box.width : 0,
            elementHeight: box ? box.height : 0,
            viewportWidth: innerWidth,
            viewportHeight: innerHeight,
            offenders,
          };
        }""",
        required_selector,
    )
    if not result["found"]:
        raise AssertionError(f"{label}: 缺少 {required_selector}")
    if result["horizontalOverflow"] > 1:
        raise AssertionError(
            f"{label}: 横向溢出 {result['horizontalOverflow']}px；"
            f"元素={json.dumps(result['offenders'], ensure_ascii=False)}"
        )
    if result["elementWidth"] <= 0 or result["elementHeight"] <= 0:
        raise AssertionError(f"{label}: {required_selector} 未渲染")
    print(label, json.dumps(result, ensure_ascii=False), flush=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        page = browser.new_page()
        page.set_default_timeout(10000)
        page.set_default_navigation_timeout(15000)
        for name, w, h in VIEWPORTS:
            page.set_viewport_size({"width": w, "height": h})

            page.goto(STATUS, wait_until="domcontentloaded")
            page.wait_for_timeout(1200)
            page.locator(".stat").first.click()
            page.wait_for_timeout(800)
            assert_layout(page, f"status-{name}", "#root")
            page.screenshot(path=str(OUT / f"status-{name}.png"), full_page=True)

            page.goto(COVER, wait_until="domcontentloaded")
            page.wait_for_timeout(500)
            assert_layout(page, f"cover-p1-{name}", "#btnEnter")
            page.screenshot(path=str(OUT / f"cover-p1-{name}.png"), full_page=True)

            page.click("#btnEnter")
            page.wait_for_timeout(350)
            page.click("#btnToMeet")
            page.wait_for_timeout(500)
            if page.locator(".char-card").count() > 0:
                page.locator(".char-card").first.click()
                page.wait_for_timeout(450)
            assert_layout(page, f"cover-p3-{name}", "#btnStart")
            start_box = page.locator("#btnStart").bounding_box()
            if not start_box or start_box["y"] >= h or start_box["y"] + start_box["height"] <= 0:
                raise AssertionError(f"cover-p3-{name}: 生成开局按钮不在可视区域")
            page.screenshot(path=str(OUT / f"cover-p3-{name}.png"), full_page=True)
        page.close()

        runtime = browser.new_page(viewport={"width": 390, "height": 844})
        runtime.set_default_timeout(10000)
        runtime.add_init_script(
            """
            window.__statusStopped = false;
            window.__statusListener = null;
            const stat_data = {
              世界: { 相遇方式: "求净上门", 场景: "圣言堂·告解室", 教会名: "圣言堂", 回合: 1 },
              初遇: {
                姓名: "牧濑红莉栖", 作品: "命运石之门", 污秽类型: "认知回响",
                污秽度: 40, 信任: 15, 好感度: 10, 堕落值: 5, 依存度: 0,
                仪式阶段: "初见", 与user关系: "陌路", 当前心态: "先验证证据",
              },
            };
            window.getAllVariables = () => ({ stat_data });
            window.getVariables = () => ({ stat_data });
            window.waitGlobalInitialized = async () => window.Mvu;
            window.waitUntil = async predicate => {
              if (!predicate()) throw new Error("mock variable unavailable");
            };
            window.Mvu = { events: { VARIABLE_UPDATE_ENDED: "mock_variable_update_ended" } };
            window.eventOn = (_event, listener) => {
              window.__statusListener = listener;
              return { stop: () => { window.__statusStopped = true; } };
            };
            """
        )
        runtime.goto(STATUS_RUNTIME, wait_until="domcontentloaded")
        runtime.wait_for_function(
            "document.getElementById('statusState')?.classList.contains('status-ready')"
        )
        assert_layout(runtime, "status-runtime-mobile", "#root")
        runtime.screenshot(path=str(OUT / "status-runtime-mobile.png"), full_page=True)
        runtime.evaluate("window.__statusListener && window.__statusListener()")
        runtime.evaluate("window.dispatchEvent(new Event('pagehide'))")
        if not runtime.evaluate("window.__statusStopped"):
            raise AssertionError("status-runtime-mobile: pagehide 未停止 MVU 监听")
        runtime.close()
        browser.close()
    expected = {
        f"{kind}-{name}.png"
        for name, _, _ in VIEWPORTS
        for kind in ("status", "cover-p1", "cover-p3")
    }
    expected.add("status-runtime-mobile.png")
    present = {shot.name for shot in OUT.glob("*.png")}
    missing = sorted(expected - present)
    if missing:
        raise AssertionError(f"缺少截图: {missing}")
    print("ok", len(expected), "screenshots")

if __name__ == "__main__":
    main()
