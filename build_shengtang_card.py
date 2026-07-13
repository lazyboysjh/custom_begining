# -*- coding: utf-8 -*-
"""从模板 JSON 生成《圣堂初遇》角色卡。"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
TEMPLATE = Path(
    os.environ.get(
        "SHENGTANG_TEMPLATE",
        r"E:\create\十国千娇\十国千娇.json",
    )
)
OUT = ROOT / "圣堂初遇.json"
CARD_NAME = "圣堂初遇"
GITHUB_REPO = os.environ.get("ST_CDN_REPO", "lazyboysjh/custom_begining")
CDN_V = os.environ.get("ST_CDN_V", "4")


def default_cdn_ref() -> str:
    if (ROOT / ".git").is_dir():
        try:
            return subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=ROOT,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    return "main"


GITHUB_REF = os.environ.get("ST_CDN_REF", "").strip() or default_cdn_ref()
CDN = f"https://testingcf.jsdelivr.net/gh/{GITHUB_REPO}@{GITHUB_REF}/dist/shengtang/ui"

# 同文档注入（禁止跨域 iframe）：否则 generate / triggerSlash 调不到酒馆 API
_INJECT_BOOT = r"""
<style>
  html,body{margin:0;padding:0;width:100%;height:__H__;min-height:__MIN__;overflow:hidden;background:transparent;}
  @media (max-width:560px){html,body{height:__H_SM__;min-height:__MIN_SM__;}}
</style>
<script>
(function () {
  var url = %URL%;
  function runScripts(doc) {
    var list = Array.prototype.slice.call(doc.querySelectorAll("script"));
    function next(i) {
      if (i >= list.length) return;
      var old = list[i];
      var s = document.createElement("script");
      if (old.src) {
        s.src = old.src;
        s.onload = function () { next(i + 1); };
        s.onerror = function () { next(i + 1); };
        document.body.appendChild(s);
      } else {
        s.textContent = old.textContent;
        document.body.appendChild(s);
        next(i + 1);
      }
    }
    next(0);
  }
  fetch(url, { cache: "no-store" })
    .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.text(); })
    .then(function (html) {
      var doc = new DOMParser().parseFromString(html, "text/html");
      doc.querySelectorAll("style").forEach(function (n) {
        document.head.appendChild(n.cloneNode(true));
      });
      doc.querySelectorAll('link[rel="stylesheet"]').forEach(function (n) {
        var l = document.createElement("link");
        l.rel = "stylesheet";
        l.href = n.href;
        if (n.crossOrigin) l.crossOrigin = n.crossOrigin;
        document.head.appendChild(l);
      });
      document.body.innerHTML = "";
      Array.prototype.slice.call(doc.body.childNodes).forEach(function (n) {
        if (n.nodeName && n.nodeName.toLowerCase() === "script") return;
        document.body.appendChild(document.importNode(n, true));
      });
      runScripts(doc);
    })
    .catch(function (e) {
      document.body.innerHTML = '<pre style="color:#c45c48;padding:12px;white-space:pre-wrap;">界面加载失败: '
        + String(e && e.message ? e.message : e) + '\\n' + url + '</pre>';
    });
})();
</script>
"""


def _shell(kind: str) -> str:
    path = "cover" if kind == "cover" else "status"
    title = "圣堂初遇封面" if kind == "cover" else "圣堂状态"
    url = f"{CDN}/{path}/index.html?v={CDN_V}"
    if kind == "cover":
        h, minh, hsm, minsm = "min(92dvh,900px)", "480px", "min(88dvh,780px)", "420px"
    else:
        h, minh, hsm, minsm = "min(72dvh,720px)", "320px", "min(78dvh,680px)", "300px"
    boot = (
        _INJECT_BOOT.replace("%URL%", json.dumps(url, ensure_ascii=False))
        .replace("__H__", h)
        .replace("__MIN__", minh)
        .replace("__H_SM__", hsm)
        .replace("__MIN_SM__", minsm)
    )
    return f"""```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;width:100%;height:{h};min-height:{minh};overflow:hidden;background:transparent;">
{boot}
</body>
</html>
```"""


COVER_HTML = _shell("cover")
STATUS_HTML = _shell("status")

VAR_LIST = """---
<status_current_variable>
{{format_message_variable::stat_data}}
</status_current_variable>"""

USER_ENTRY = """<{{user}}>
  姓名、身份、表面作风、私下心思见 主角 变量。正文称 {{user}}。
  默认教堂牧师，能净化污秽；仪式可真实驱除，也可被借机越界。
</{{user}}>"""

MVU_FORMAT = """---
变量输出格式:
  rule:
    - 每次回复末尾输出一个 <UpdateVariable>；先写剧情再输出变量块
    - 世界.相遇方式 开局后只读
    - 主角姓名/身份/能力摘要 开局后只读
    - 初遇姓名/作品/是否自定义 开局后只读
    - 污秽度/信任/好感度/堕落值/依存度 用 replace 或 delta，范围 0-100
    - 按 worldbook「数值影响」区间写反应，勿每句报数
    - JSON Patch 操作为 replace / delta / insert / remove
  format: |-
    <UpdateVariable>
    <Analysis>$(IN ENGLISH, terse bullets)
    - [Scene] location / ritual phase
    - [Filth/Trust/Favor/Fall/Dep] value changes
    - [Patch] JSON Patch ops
    </Analysis>
    <JSONPatch>
    [ {"op":"replace","path":"/初遇/好感度","value":18}, {"op":"replace","path":"/初遇/堕落值","value":8} ]
    </JSONPatch>
    </UpdateVariable>"""


def wb_entry(
    comment,
    content,
    entry_id,
    *,
    constant=False,
    selective=False,
    keys=None,
    position="before_char",
    depth=0,
    order=100,
    enabled=True,
):
    scan_depth = None if constant else 2
    return {
        "id": entry_id,
        "keys": keys or [],
        "secondary_keys": [],
        "comment": comment,
        "content": content,
        "constant": constant,
        "selective": selective,
        "insertion_order": order,
        "enabled": enabled,
        "position": position,
        "depth": depth,
        "scan_depth": scan_depth,
        "use_regex": False,
        "extensions": {
            "position": 0,
            "exclude_recursion": False,
            "prevent_recursion": True,
            "probability": 100,
            "display_index": entry_id,
        },
    }


def dump_initvar_block(obj, indent=0) -> list[str]:
    pad = "  " * indent
    lines: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}:")
                lines.extend(dump_initvar_block(v, indent + 1))
            else:
                if isinstance(v, bool):
                    lines.append(f"{pad}{k}: {'true' if v else 'false'}")
                elif v == "":
                    lines.append(f"{pad}{k}: ''")
                else:
                    lines.append(f"{pad}{k}: {v}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                lines.extend(dump_initvar_block(item, indent))
            else:
                lines.append(f"{pad}- {item}")
    else:
        lines.append(f"{pad}{obj}")
    return lines


def build_schema_script() -> str:
    return (ROOT / "plot/schema.mvu.js").read_text(encoding="utf-8")


def build_initvar() -> str:
    data = yaml.safe_load((ROOT / "plot/initvar.yaml").read_text(encoding="utf-8"))
    lines = ["<initvar>", *dump_initvar_block(data), "</initvar>"]
    return "\n".join(lines)


def build_mvu_update() -> str:
    raw = (ROOT / "plot/mvu_update.yaml").read_text(encoding="utf-8")
    if raw.startswith("---"):
        raw = raw.split("---", 1)[-1]
    data = yaml.safe_load(raw) or {}
    rules = data.get("变量更新规则") or data
    lines = ["<变量更新规则>"]
    lines.extend(dump_initvar_block(rules))
    lines.append("</变量更新规则>")
    return "\n".join(lines)


def load_characters() -> list[dict]:
    data = yaml.safe_load((ROOT / "plot/characters.yaml").read_text(encoding="utf-8")) or {}
    chars = data.get("characters") or []
    for c in chars:
        c["aliases"] = [str(a) for a in (c.get("aliases") or [])]
    return chars


def load_meeting_modes() -> list[dict]:
    data = yaml.safe_load((ROOT / "plot/meeting_modes.yaml").read_text(encoding="utf-8")) or {}
    return list(data.get("modes") or [])


def build_worldbook_entries() -> list:
    entries = []
    entry_id = 0

    def add(comment, content, **kw):
        nonlocal entry_id
        entries.append(wb_entry(comment, content, entry_id, **kw))
        entry_id += 1

    add("{{user}}", USER_ENTRY, constant=True, position="before_char", depth=4, order=3)
    add(
        "===变量开始===",
        "",
        constant=False,
        position="at_depth",
        depth=0,
        order=198,
        enabled=False,
    )
    add(
        "[initvar]变量初始化勿开",
        build_initvar(),
        constant=True,
        position="at_depth",
        depth=4,
        order=200,
        enabled=False,
    )
    add("变量列表", VAR_LIST.strip(), constant=True, position="at_depth", depth=0, order=199)
    add(
        "[mvu_update]变量更新规则",
        build_mvu_update(),
        constant=True,
        position="at_depth",
        depth=0,
        order=200,
    )
    add(
        "[mvu_update]变量输出格式",
        MVU_FORMAT.strip(),
        constant=True,
        position="at_depth",
        depth=0,
        order=201,
    )
    add(
        "===变量结束===",
        "",
        constant=False,
        position="at_depth",
        depth=0,
        order=202,
        enabled=False,
    )

    add(
        "世界观",
        (ROOT / "worldbook/00_世界观.md").read_text(encoding="utf-8"),
        constant=True,
        position="before_char",
        depth=4,
        order=1,
    )
    add(
        "净化与污秽",
        (ROOT / "worldbook/01_净化与污秽.md").read_text(encoding="utf-8"),
        constant=True,
        position="before_char",
        depth=4,
        order=2,
    )
    add(
        "写作与人设规则",
        (ROOT / "worldbook/02_写作与人设规则.md").read_text(encoding="utf-8"),
        constant=True,
        position="before_char",
        depth=4,
        order=5,
    )
    add(
        "数值影响",
        (ROOT / "worldbook/03_数值影响.md").read_text(encoding="utf-8"),
        constant=True,
        position="before_char",
        depth=4,
        order=6,
    )

    for i, c in enumerate(load_characters()):
        name = c["name"]
        path = ROOT / "worldbook" / "角色" / f"{name}.md"
        content = path.read_text(encoding="utf-8") if path.is_file() else f"角色档案:\n  基本信息:\n    姓名: {name}\n"
        keys = [name, *c.get("aliases", [])]
        # dedupe keep order
        seen = set()
        keys = [k for k in keys if not (k in seen or seen.add(k))]
        add(
            f"角色_{name}",
            content,
            constant=False,
            selective=True,
            keys=keys,
            position="before_char",
            depth=4,
            order=50 + i,
        )

    return entries


def sync_cover_assets() -> None:
    modes = load_meeting_modes()
    chars = load_characters()
    cover = ROOT / "src/shengtang/ui/cover/index.html"
    text = cover.read_text(encoding="utf-8")

    modes_js = "const MEETING_MODES = " + json.dumps(modes, ensure_ascii=False, indent=2) + ";"
    chars_js = "const CHARACTERS = " + json.dumps(chars, ensure_ascii=False, indent=2) + ";"

    text = re.sub(
        r"/\* === SYNC_BEGIN:MEETING_MODES === \*/.*?/\* === SYNC_END:MEETING_MODES === \*/",
        lambda _m: "/* === SYNC_BEGIN:MEETING_MODES === */\n" + modes_js + "\n/* === SYNC_END:MEETING_MODES === */",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"/\* === SYNC_BEGIN:CHARACTERS === \*/.*?/\* === SYNC_END:CHARACTERS === \*/",
        lambda _m: "/* === SYNC_BEGIN:CHARACTERS === */\n" + chars_js + "\n/* === SYNC_END:CHARACTERS === */",
        text,
        count=1,
        flags=re.S,
    )
    cover.write_text(text, encoding="utf-8")
    print(f"synced cover data: {len(modes)} modes, {len(chars)} characters")

    # 状态栏抽卡角色池（精简字段）
    roster = [
        {
            "id": c.get("id"),
            "name": c.get("name"),
            "work": c.get("work"),
            "age_note": c.get("age_note"),
            "appearance": c.get("appearance") or "",
            "blurb": c.get("blurb") or "",
            "intro": c.get("intro") or "",
            "filth_seed": c.get("filth_seed"),
        }
        for c in chars
    ]
    status = ROOT / "src/shengtang/ui/status/index.html"
    st = status.read_text(encoding="utf-8")
    roster_js = "const ROSTER = " + json.dumps(roster, ensure_ascii=False, indent=2) + ";"
    st2, n = re.subn(
        r"/\* === SYNC_BEGIN:ROSTER === \*/.*?/\* === SYNC_END:ROSTER === \*/",
        "/* === SYNC_BEGIN:ROSTER === */\n" + roster_js + "\n/* === SYNC_END:ROSTER === */",
        st,
        count=1,
        flags=re.S,
    )
    if not n:
        raise SystemExit("status ROSTER sync markers missing")
    status.write_text(st2, encoding="utf-8")
    print(f"synced status roster: {len(roster)}")


def sync_static_dist() -> None:
    for sub in ("cover", "status"):
        src = ROOT / "src/shengtang/ui" / sub / "index.html"
        dst_dir = ROOT / "dist/shengtang/ui" / sub
        dst_dir.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            shutil.copy2(src, dst_dir / "index.html")
    print("copied static UI to dist/shengtang/ui")


def patch_regex_scripts(card: dict) -> None:
    scripts = card["data"]["extensions"].get("regex_scripts") or []
    for rs in scripts:
        sn = rs.get("scriptName", "")
        find = rs.get("findRegex", "")
        if sn == "显示-状态栏美化" or ("状态栏" in sn and "美化" in sn):
            rs["replaceString"] = STATUS_HTML
        elif "StatusPlaceHolderImpl" in find:
            if "隐藏" in sn or "提示词" in sn:
                rs["replaceString"] = ""
            else:
                rs["replaceString"] = STATUS_HTML


def patch_tavern_helper_scripts(card: dict) -> None:
    scripts = card["data"]["extensions"].get("tavern_helper", {}).get("scripts") or []
    for script in scripts:
        if script.get("name") == "变量结构":
            script["content"] = build_schema_script()


def main() -> None:
    if not TEMPLATE.is_file():
        raise SystemExit(f"模板不存在: {TEMPLATE}\n请设置 SHENGTANG_TEMPLATE")

    sync_cover_assets()
    sync_static_dist()

    card = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    card["name"] = CARD_NAME
    card["description"] = "捏同人开局：圣堂牧师 × 热门动漫女性初遇。净化真实成立，亦可借仪式越界。"
    card["personality"] = ""
    card["scenario"] = "圣言堂。{{user}}是能净化污秽的牧师；初遇一名成年二次元女性，按封面所选相遇方式开局。"
    card["first_mes"] = COVER_HTML
    card["mes_example"] = ""
    card["creatorcomment"] = "圣堂初遇 / custom_begining"
    card["tags"] = ["综漫", "圣堂", "净化", "开局捏人"]

    data = card.setdefault("data", {})
    data["name"] = CARD_NAME
    data["description"] = card["description"]
    data["personality"] = ""
    data["scenario"] = card["scenario"]
    data["first_mes"] = COVER_HTML
    data["mes_example"] = ""
    data["creator_notes"] = card["creatorcomment"]
    data["system_prompt"] = ""
    data["post_history_instructions"] = ""
    data["tags"] = card["tags"]
    data["creator"] = "lazyboysjh"
    data["character_version"] = "0.1.0"
    data["alternate_greetings"] = []

    ext = data.setdefault("extensions", {})
    ext["world"] = CARD_NAME

    book = data.setdefault("character_book", {})
    book["name"] = CARD_NAME
    book["entries"] = build_worldbook_entries()

    patch_tavern_helper_scripts(card)
    patch_regex_scripts(card)

    OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    print(f"CDN={CDN}")


if __name__ == "__main__":
    main()
