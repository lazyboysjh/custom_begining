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
TEMPLATE = ROOT / "templates" / "shengtang_base.json"
OUT = ROOT / "圣堂初遇.json"
CARD_NAME = "圣堂初遇"
GITHUB_REPO = os.environ.get("ST_CDN_REPO", "lazyboysjh/custom_begining")
CDN_V = os.environ.get("ST_CDN_V", "7")


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
# 高度用 width + aspect-ratio，禁止 vh/dvh/min-height 撑破消息楼层
_INJECT_BOOT = r"""
<style>
  html,body{margin:0;padding:0;width:100%;__SIZE__overflow:__OVERFLOW__;background:transparent;}
  @media (max-width:560px){html,body{__SIZE_SM__}}
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
    # 封面自身滚动，保持可视框；状态栏由内容自然撑高，不能用固定比例裁切。
    if kind == "cover":
        size, size_sm, overflow = "aspect-ratio:16 / 9;", "aspect-ratio:9 / 16;", "hidden"
        body_style = "margin:0;padding:0;width:100%;aspect-ratio:16/9;overflow:hidden;background:transparent;"
    else:
        size, size_sm, overflow = "", "", "visible"
        body_style = "margin:0;padding:0;width:100%;overflow:visible;background:transparent;"
    boot = (
        _INJECT_BOOT.replace("%URL%", json.dumps(url, ensure_ascii=False))
        .replace("__SIZE__", size)
        .replace("__SIZE_SM__", size_sm)
        .replace("__OVERFLOW__", overflow)
    )
    return f"""```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <title>{title}</title>
</head>
<body style="{body_style}">
{boot}
</body>
</html>
```"""


COVER_HTML = _shell("cover")
STATUS_HTML = _shell("status")

VAR_LIST = """---
<status_current_variables>
{{format_message_variable::stat_data}}
</status_current_variables>"""

USER_ENTRY = """<{{user}}>
  姓名、身份、表面作风、私下心思见 主角 变量。正文称 {{user}}。
  默认教堂牧师，能净化污秽；仪式可真实驱除，也可被借机越界。
</{{user}}>"""

PROFILE_RULES = """<人设演绎总则>
  指导（不是设定复述）:
  - 按「世界.出场角色」与「角色.[姓名]」逐人读取档案；数值只调犹豫幅度，不改性格底色。
  - 每轮先写清她自己的目标/风险判断，再写对{{user}}的反应；禁止整段围着讨好转。
  - 净化有效 ≠ 可爱可靠；可承认「有用」，不得跳到崇拜/献身/秒信。
  - 开局无旧识；可拒绝、拖延、试探、讨价还价；牧师身份不提高服从。
  - 保留原作核心关系；{{user}}不得凭主角光环取代家人、恋人、敌人或职责。
  - 无充分事件时禁捷径词：「好厉害」「只有你」「我愿意为你」「从见面起就…」。
  - 外貌只写可辨识差异特征；禁精致五官/绝美/倾国等万能美人套话。
  - 禁止元叙事、系统自指、提醒「在玩角色卡」。
</人设演绎总则>"""

# 写卡知识库「变量输出格式」固定骨架；卡专属只读/步长写在 [mvu_update]变量更新规则
MVU_FORMAT = """---
变量输出格式:
  rule:
    - you must output the update analysis and the actual update commands at once in the end of the next reply
    - the update commands works like the **JSON Patch (RFC 6902)** standard, must be a valid JSON array containing operation objects, but supports the following operations instead:
      - replace: replace the value of existing paths
      - delta: update the value of existing number paths by a delta value
      - insert: insert new items into an object or array (using `-` as array index intends appending to the end)
      - remove
      - move
    - don't update field names starts with `_` as they are readonly, such as `_变量`
  format: |-
    <UpdateVariable>
    <Analysis>$(IN ENGLISH, no more than 80 words)
    - ${calculate time passed: ...}
    - ${decide whether dramatic updates are allowed as it's in a special case or the time passed is more than usual: yes/no}
    - ${analyze every variable based on its corresponding `check`, according only to current reply instead of previous plots: ...}
    </Analysis>
    <JSONPatch>
    [
      { "op": "replace", "path": "${/path/to/variable}", "value": "${new_value}" },
      { "op": "delta", "path": "${/path/to/number/variable}", "value": "${positive_or_negative_delta}" },
      { "op": "insert", "path": "${/path/to/object/new_key}", "value": "${new_value}" },
      { "op": "insert", "path": "${/path/to/array/-}", "value": "${new_value}" },
      { "op": "remove", "path": "${/path/to/object/key}" },
      { "op": "remove", "path": "${/path/to/array/0}" },
      { "op": "move", "from": "${/path/to/variable}", "to": "${/path/to/another/path}" }
    ]
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
    # before/after_char 的 depth 无意义，统一 0；仅 at_depth 使用 depth
    store_depth = depth if position == "at_depth" else 0
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
        "depth": store_depth,
        "scan_depth": scan_depth,
        "use_regex": False,
        "extensions": {
            "position": 0,
            # 写卡知识库：不可递归 + 防止进一步递归 必须同时勾选
            "exclude_recursion": True,
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


def load_character_registry() -> dict:
    path = ROOT / "plot/character_sources.yaml"
    if not path.is_file():
        return {"base_roster": "characters.yaml", "batches": []}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def iter_character_payloads() -> list[tuple[Path, dict]]:
    registry = load_character_registry()
    plot_dir = ROOT / "plot"
    base_path = plot_dir / str(registry.get("base_roster") or "characters.yaml")
    payloads = [(base_path, yaml.safe_load(base_path.read_text(encoding="utf-8")) or {})]
    batch_dir = plot_dir / str(registry.get("batch_directory") or "character_batches")
    for item in registry.get("batches") or []:
        path = batch_dir / str(item.get("path") or "")
        if not path.is_file():
            raise SystemExit(f"character batch missing: {path.relative_to(ROOT)}")
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        expected = int(item.get("expected_count") or 0)
        actual = len(payload.get("characters") or [])
        if expected and actual != expected:
            raise SystemExit(f"character batch count mismatch: {path.name} ({actual} != {expected})")
        payloads.append((path, payload))
    return payloads


def load_characters() -> list[dict]:
    chars: list[dict] = []
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for path, payload in iter_character_payloads():
        for raw in payload.get("characters") or []:
            char = dict(raw)
            char["aliases"] = [str(alias) for alias in (char.get("aliases") or [])]
            char_id = str(char.get("id") or "").strip()
            name = str(char.get("name") or "").strip()
            if not char_id or not name:
                raise SystemExit(f"character missing id/name: {path.relative_to(ROOT)}")
            if char_id in seen_ids or name in seen_names:
                raise SystemExit(f"duplicate character id/name: {char_id} / {name}")
            seen_ids.add(char_id)
            seen_names.add(name)
            chars.append(char)
    return chars


def load_character_sources() -> dict[str, dict]:
    sources: dict[str, dict] = {}
    for path, payload in iter_character_payloads()[1:]:
        for char_id, source in (payload.get("sources") or {}).items():
            key = str(char_id).strip()
            if key in sources:
                raise SystemExit(f"duplicate character source: {key} ({path.relative_to(ROOT)})")
            sources[key] = dict(source or {})
    return sources


def validate_character_catalog(chars: list[dict], sources: dict[str, dict]) -> None:
    registry = load_character_registry()
    base_path = ROOT / "plot" / str(registry.get("base_roster") or "characters.yaml")
    base = yaml.safe_load(base_path.read_text(encoding="utf-8")) or {}
    base_ids = {str(char.get("id") or "") for char in (base.get("characters") or [])}
    added = [char for char in chars if char["id"] not in base_ids]
    expected_total = len(base_ids) + sum(
        int(item.get("expected_count") or 0) for item in (registry.get("batches") or [])
    )
    if len(chars) != expected_total:
        raise SystemExit(f"character catalog count mismatch: {len(chars)} != {expected_total}")
    if set(sources) != {char["id"] for char in added}:
        raise SystemExit("character source ids do not exactly match the added roster")

    required_text = ("name", "work", "appearance", "blurb", "intro", "work_intro", "filth_seed")
    alias_owners: dict[str, str] = {}
    for char in chars:
        for field in required_text:
            if not str(char.get(field) or "").strip():
                raise SystemExit(f"character field missing: {char['id']}.{field}")
        for alias in [char["name"], *(char.get("aliases") or [])]:
            key = str(alias).strip().casefold()
            if not key:
                continue
            owner = alias_owners.setdefault(key, char["id"])
            if owner != char["id"]:
                raise SystemExit(f"character alias collision: {alias} ({owner} / {char['id']})")

    for char in added:
        source = sources[char["id"]]
        if not source.get("category") or not source.get("primary") or not source.get("notes"):
            raise SystemExit(f"character source incomplete: {char['id']}")


def load_meeting_modes() -> list[dict]:
    data = yaml.safe_load((ROOT / "plot/meeting_modes.yaml").read_text(encoding="utf-8")) or {}
    return list(data.get("modes") or [])


def load_opening_options() -> dict[str, list[dict]]:
    data = yaml.safe_load((ROOT / "plot/opening_options.yaml").read_text(encoding="utf-8")) or {}
    required = (
        "story_types",
        "atmospheres",
        "eras",
        "sanctum_forms",
        "integration_modes",
        "ability_presets",
    )
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise SystemExit(f"opening options missing: {', '.join(missing)}")
    return {key: list(data[key]) for key in required}


def build_character_overview(chars: list[dict]) -> str:
    lines = [
        "<角色速览>",
        "  本卡为多角色池；开局只选一名初遇，详细档案绿灯触发（关键词=姓名/别名）。",
        "  当前在场人物以「世界.出场角色」为准；每人状态独立存于「角色.[姓名]」。",
        "  演绎须贴各人档案口吻与底线，禁止串戏与万能温柔模板。",
        "",
        "  角色池:",
    ]
    for c in chars:
        name = c.get("name") or ""
        work = c.get("work") or ""
        blurb = (c.get("blurb") or "").strip().replace("\n", " ")
        if len(blurb) > 36:
            blurb = blurb[:36] + "…"
        lines.append(f"  - {name}（{work}）：{blurb}")
    lines.append("</角色速览>")
    return "\n".join(lines)


def render_character_profile(c: dict) -> str:
    name = c["name"]
    aliases = "、".join(str(a) for a in (c.get("aliases") or []))
    age = c.get("age_note") or ""
    work = c.get("work") or ""
    year = c.get("year")
    work_line = f"{work}（约 {year} 起热度）" if year else work
    intro = (c.get("intro") or c.get("blurb") or "").strip()
    appearance = (c.get("appearance") or "").strip()
    work_intro = (c.get("work_intro") or "").strip()
    background = c.get("background") or []
    if isinstance(background, str):
        background = [background]
    relations = c.get("relations") or []
    if isinstance(relations, str):
        relations = [relations]
    filth = (c.get("filth_seed") or "").strip()
    blurb = (c.get("blurb") or "").strip()

    # 演绎锚点：从既有字段提炼，避免空喊「原作感」
    voice_bits = [r for r in relations if r and "与{{user}}" not in r and "开局" not in r]
    if not voice_bits and blurb:
        voice_bits = [blurb]
    drive_bits = [str(b) for b in background if b][:2]
    drive_bits.extend(r for r in relations if r and "与{{user}}" not in r and r not in drive_bits)
    hard_lines = [
        f"遮住姓名也应能认出是「{name}」：外貌与口吻不得换成万能美人/万能温柔",
        "开局与{{user}}无旧识；低信任时可持续戒备、质疑、拒绝私密检查",
        "数值只调反应强度；不可因好感/堕落升高而丢掉本条口吻与职业惯性",
        "保留原作核心关系与独立目标；{{user}}不能仅凭主角身份取代、压过或抹除它们",
        "不奉承{{user}}，不凭空认定其正确、强大或有魅力；关系变化必须对应已发生事件",
    ]
    loyalty_blob = "\n".join([intro, blurb, "\n".join(background), "\n".join(relations)])
    if any(k in loyalty_blob for k in ("主人", "Darling", "人妻", "忠诚", "影子大人")):
        hard_lines.append(
            "原作忠诚/亲密对象不可因一次净化或救助转移给{{user}}；开局最多试探或利用，禁止秒改称呼与献身"
        )
    if filth:
        hard_lines.append(f"污秽发作优先挂钩种子：{filth}")

    lines = [
        "角色档案:",
        "  基本信息:",
        f"    姓名: {name}",
        f"    别名: {aliases}",
        "    性别: 女",
        f"    作品: {work_line}",
    ]
    if age:
        lines.append(f"    年龄: {age}")
    lines.extend([
        f"    身份: {blurb or '见原作；本卡开局为初遇对象'}",
        "    与{{user}}关系: 开局无旧识",
        "",
        "  角色介绍:",
        f"    {intro}",
        "",
        "  外貌特征:",
        f"    - {appearance}" if appearance else "    - （见原作辨识特征）",
        "",
        "  背景设定:",
    ])
    if work_intro:
        lines.append(f"    作品简介: {work_intro}")
    if background:
        lines.append("    角色要点:")
        for b in background:
            lines.append(f"    - {b}")
    if filth:
        lines.append(f"    污秽种子: {filth}")
    lines.append("")
    lines.append("  关系设定:")
    if relations:
        for r in relations:
            lines.append(f"    - {r}")
    else:
        lines.append("    - 与{{user}}：开局无旧识")
    lines.append("")
    lines.append("  演绎锚点:")
    lines.append("    行动驱力:")
    for d in drive_bits[:4]:
        lines.append(f"    - {d}")
    lines.append("    口吻:")
    for v in voice_bits[:4]:
        lines.append(f"    - {v}")
    lines.append("    不可违背:")
    for h in hard_lines:
        lines.append(f"    - {h}")
    lines.append("")
    return "\n".join(lines)


def build_worldbook_entries() -> list:
    entries = []
    entry_id = 0
    chars = load_characters()

    def add(comment, content, **kw):
        nonlocal entry_id
        entries.append(wb_entry(comment, content, entry_id, **kw))
        entry_id += 1

    add("{{user}}", USER_ENTRY, constant=True, position="before_char", order=3)
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
    # MVU自查：变量列表 / 更新规则 / 输出格式 → D0，顺序 200
    add("变量列表", VAR_LIST.strip(), constant=True, position="at_depth", depth=0, order=200)
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
        order=200,
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

    # 大世界观：角色定义前 · 蓝灯
    add(
        "世界观",
        (ROOT / "worldbook/00_世界观.md").read_text(encoding="utf-8"),
        constant=True,
        position="before_char",
        order=1,
    )
    add(
        "净化与污秽",
        (ROOT / "worldbook/01_净化与污秽.md").read_text(encoding="utf-8"),
        constant=True,
        position="before_char",
        order=2,
    )
    add(
        "角色速览",
        build_character_overview(chars),
        constant=True,
        position="before_char",
        order=4,
    )
    # 写作指导 / 数值反应：D0（知识库：指导类放 D0，不塞设定位）
    add(
        "写作与人设规则",
        (ROOT / "worldbook/02_写作与人设规则.md").read_text(encoding="utf-8"),
        constant=True,
        position="at_depth",
        depth=0,
        order=1,
    )
    add(
        "数值影响",
        (ROOT / "worldbook/03_数值影响.md").read_text(encoding="utf-8"),
        constant=True,
        position="at_depth",
        depth=0,
        order=2,
    )
    add(
        "人设演绎总则",
        PROFILE_RULES.strip(),
        constant=True,
        position="at_depth",
        depth=0,
        order=3,
    )

    # 多角色卡：角色详细 → 角色定义后 · 绿灯 · 顺序约 99
    # scan_depth 提到 4，降低「姓名刚离开近2楼就丢档案」导致的 OOC
    profile_dir = ROOT / "worldbook" / "角色"
    profile_dir.mkdir(parents=True, exist_ok=True)
    expected_profiles = {f"{c['name']}.md" for c in chars}
    for stale in profile_dir.glob("*.md"):
        if stale.name not in expected_profiles:
            stale.unlink()
    for i, c in enumerate(chars):
        name = c["name"]
        path = profile_dir / f"{name}.md"
        content = render_character_profile(c)
        path.write_text(content, encoding="utf-8")
        keys = [name, *c.get("aliases", [])]
        seen = set()
        keys = [k for k in keys if not (k in seen or seen.add(k))]
        entry = wb_entry(
            f"角色_{name}",
            content,
            entry_id,
            constant=False,
            selective=True,
            keys=keys,
            position="after_char",
            order=99,
        )
        entry["scan_depth"] = 4
        entries.append(entry)
        entry_id += 1

    return entries


def sync_cover_assets() -> None:
    options = load_opening_options()
    chars = load_characters()
    cover = ROOT / "src/shengtang/ui/cover/index.html"
    text = cover.read_text(encoding="utf-8")

    options_js = "const OPENING_OPTIONS = " + json.dumps(options, ensure_ascii=False, indent=2) + ";"
    chars_js = "const CHARACTERS = " + json.dumps(chars, ensure_ascii=False, indent=2) + ";"

    text, options_count = re.subn(
        r"/\* === SYNC_BEGIN:OPENING_OPTIONS === \*/.*?/\* === SYNC_END:OPENING_OPTIONS === \*/",
        lambda _m: "/* === SYNC_BEGIN:OPENING_OPTIONS === */\n" + options_js + "\n/* === SYNC_END:OPENING_OPTIONS === */",
        text,
        count=1,
        flags=re.S,
    )
    text, chars_count = re.subn(
        r"/\* === SYNC_BEGIN:CHARACTERS === \*/.*?/\* === SYNC_END:CHARACTERS === \*/",
        lambda _m: "/* === SYNC_BEGIN:CHARACTERS === */\n" + chars_js + "\n/* === SYNC_END:CHARACTERS === */",
        text,
        count=1,
        flags=re.S,
    )
    if options_count != 1 or chars_count != 1:
        raise SystemExit(
            f"cover sync markers invalid: opening_options={options_count}, characters={chars_count}"
        )
    cover.write_text(text, encoding="utf-8")
    print(f"synced cover data: {len(options['story_types'])} story types, {len(chars)} characters")

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
    def regex(
        id_: str,
        name: str,
        find: str,
        replace: str,
        *,
        markdown: bool,
        prompt: bool,
        min_depth=None,
        max_depth=None,
    ) -> dict:
        return {
            "id": id_,
            "scriptName": name,
            "findRegex": find,
            "replaceString": replace,
            "trimStrings": [],
            "placement": [2],
            "disabled": False,
            "markdownOnly": markdown,
            "promptOnly": prompt,
            "runOnEdit": True,
            "substituteRegex": 0,
            "minDepth": min_depth,
            "maxDepth": max_depth,
        }

    card["data"]["extensions"]["regex_scripts"] = [
        regex(
            "shengtang-cover-keep",
            "显示-封面HTML后移除状态栏占位",
            r"/(```html[\s\S]*?<\/html>\s*```)\s*^\s*<StatusPlaceHolderImpl\s*\/>\s*$/gim",
            "$1",
            markdown=True,
            prompt=False,
        ),
        regex(
            "shengtang-status-render",
            "显示-状态栏美化",
            r"/<StatusPlaceHolderImpl\s*\/>/gi",
            STATUS_HTML,
            markdown=True,
            prompt=False,
        ),
        regex(
            "shengtang-hide-update-display",
            "显示-隐藏变量更新块",
            r"/^\s*<UpdateVariable(?:variable)?>[\s\S]*?^\s*<\/UpdateVariable(?:variable)?>\s*$/gim",
            "",
            markdown=True,
            prompt=False,
        ),
        regex(
            "shengtang-hide-status-prompt",
            "提示词-隐藏状态栏占位",
            r"/^\s*<StatusPlaceHolderImpl\s*\/>\s*$/gim",
            "",
            markdown=False,
            prompt=True,
        ),
        regex(
            "shengtang-limit-update-prompt",
            "提示词-仅发送近3楼变量",
            r"/^\s*<UpdateVariable(?:variable)?>[\s\S]*?^\s*<\/UpdateVariable(?:variable)?>\s*$/gim",
            "",
            markdown=False,
            prompt=True,
            min_depth=6,
        ),
        regex(
            "shengtang-hide-ui-prompt",
            "提示词-隐藏界面CDN壳",
            r"/```html[\s\S]*?dist\/shengtang\/ui\/[\s\S]*?```/gim",
            "",
            markdown=False,
            prompt=True,
        ),
    ]


def patch_tavern_helper_scripts(card: dict) -> None:
    def script(id_: str, name: str, content: str, buttons: list[dict]) -> dict:
        return {
            "type": "script",
            "enabled": True,
            "name": name,
            "id": id_,
            "content": content,
            "info": "",
            "button": {"enabled": True, "buttons": buttons},
            "data": {},
            "export_with": {"data": True, "button": True},
        }

    card["data"]["extensions"]["tavern_helper"] = {
        "scripts": [
            script("shengtang-schema", "变量结构", build_schema_script(), []),
            script(
                "shengtang-mvu",
                "MVUbeta",
                "import 'https://testingcf.jsdelivr.net/gh/MagicalAstrogy/MagVarUpdate/artifact/bundle.js';",
                [
                    {"name": "重新处理变量", "visible": True},
                    {"name": "重新读取初始变量", "visible": True},
                    {"name": "清除旧楼层变量", "visible": False},
                    {"name": "快照楼层", "visible": False},
                    {"name": "重演楼层", "visible": False},
                    {"name": "重试额外模型解析", "visible": False},
                ],
            ),
        ]
    }


def main() -> None:
    if not TEMPLATE.is_file():
        raise SystemExit(f"模板不存在: {TEMPLATE}\n请设置 SHENGTANG_TEMPLATE")

    validate_character_catalog(load_characters(), load_character_sources())
    sync_cover_assets()
    sync_static_dist()

    card = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    card["name"] = CARD_NAME
    card["description"] = f"跨时代随机初遇：设定{{{{user}}}}的净化能力，由圣堂从{len(load_characters())}名女性角色中揭晓来客与故事。"
    card["personality"] = ""
    card["scenario"] = "圣堂会随时代改变外在形态，但始终保留净化体系、跨界节点、仪式规则与长期据点。{{user}}设定能力后，其余开局要素随机生成。"
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
    data["character_version"] = "0.2.0"
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
