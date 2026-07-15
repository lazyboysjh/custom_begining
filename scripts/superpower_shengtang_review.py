# -*- coding: utf-8 -*-
"""Superpower 审查：圣堂初遇角色资料 × 写卡知识库规范 × 卡/CDN 就绪。"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build_shengtang_card import load_characters

WB_DIR = ROOT / "worldbook" / "角色"
CARD = ROOT / "圣堂初遇.json"

# 外貌万能废话 / 主观美颜
APPEARANCE_FILLER = re.compile(
    r"精致|白皙|好看|美丽|漂亮|绝美|倾国|亭亭|匀称|优雅气质|完美容颜|肤如凝脂|桃花眼"
)
# 关系抽象词
REL_ABSTRACT = re.compile(r"深厚的感情|关系很好|彼此信任|羁绊深厚|心灵相通")
# 性格标签堆砌（角色介绍里大量纯标签可警告）
TRAIT_SPAM = re.compile(r"(温柔|傲娇|毒舌|高冷|元气|腹黑)(、|,|，|/)")


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()


def run_raw(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout or ""


def section(body: str, name: str) -> str:
    m = re.search(rf"^  {re.escape(name)}:\s*\n([\s\S]*?)(?=^  \S|\Z)", body, re.M)
    return m.group(1) if m else ""


def main() -> int:
    errs: list[str] = []
    warns: list[str] = []
    oks: list[str] = []

    chars = load_characters()
    oks.append(f"组合角色目录共 {len(chars)} 人")

    # --- 知识库四段结构（世界书 md）---
    required_secs = ["基本信息", "外貌特征", "背景设定", "关系设定"]
    # 本卡额外有「角色介绍」：允许，但不替代四段
    for c in chars:
        name = c["name"]
        path = WB_DIR / f"{name}.md"
        if not path.is_file():
            errs.append(f"{name}: 缺 worldbook/角色/{name}.md")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.strip().startswith("角色档案:"):
            errs.append(f"{name}: 世界书不以「角色档案:」开头")
        for sec in required_secs:
            if f"  {sec}:" not in text:
                errs.append(f"{name}: 缺分段「{sec}」")
        # 基本信息必要字段
        basic = section(text.replace("角色档案:\n", ""), "基本信息") if "角色档案:" in text else ""
        # simpler checks on full text
        for key in ("姓名:", "性别:", "作品:", "年龄:", "与{{user}}关系:"):
            if key not in text:
                errs.append(f"{name}: 基本信息缺 {key}")

        # 角色介绍允许存在（本卡需求）；性格标签应主要在介绍里，不在「基本信息」
        if "  角色介绍:" not in text:
            warns.append(f"{name}: 无「角色介绍」分段（本卡建议有）")
        else:
            # 介绍里不要只剩标签
            intro_sec = section(text.split("角色档案:\n", 1)[-1], "角色介绍")
            if intro_sec and len(re.findall(r"[\u4e00-\u9fff]", intro_sec)) < 80:
                errs.append(f"{name}: 角色介绍有效汉字过少")

        # 外貌：特征向
        app_sec = ""
        mapp = re.search(r"外貌特征:\s*\n([\s\S]*?)(?=^  \S|\Z)", text, re.M)
        if mapp:
            app_sec = mapp.group(1)
            if APPEARANCE_FILLER.search(app_sec):
                warns.append(f"{name}: 外貌含万能美颜词")
            if "精致的脸" in app_sec or "白皙的皮肤" in app_sec:
                errs.append(f"{name}: 外貌万能废话句")

        intro = c.get("intro") or ""
        if len(intro) < 80:
            errs.append(f"{name}: intro 过短（{len(intro)}字），需详细介绍")
        elif len(intro) < 120:
            warns.append(f"{name}: intro 偏短（{len(intro)}字）")

        app = c.get("appearance") or ""
        if APPEARANCE_FILLER.search(app):
            warns.append(f"{name}: 外貌含万能美颜词 → {APPEARANCE_FILLER.findall(app)}")
        if len(app) < 20:
            errs.append(f"{name}: 外貌过短，辨识度不足")

        bg = c.get("background") or []
        if len(bg) < 2:
            errs.append(f"{name}: 背景要点 < 2")
        if not c.get("filth_seed"):
            errs.append(f"{name}: 缺污秽种子")
        if not c.get("work_intro"):
            errs.append(f"{name}: 缺作品简介")

        aliases = c.get("aliases") or []
        if not aliases:
            warns.append(f"{name}: 无别名，绿灯触发可能偏窄")

        # 关系设定抽象检查
        rel = ""
        m = re.search(r"关系设定:\s*\n([\s\S]*?)(?=\Z)", text)
        if m:
            rel = m.group(1)
            if REL_ABSTRACT.search(rel):
                warns.append(f"{name}: 关系设定含抽象句")
            if "与{{user}}" not in rel and "与{{user}}" not in text:
                warns.append(f"{name}: 关系设定未点明与 user 开局关系")

    # 重复作品（非错误，提示）
    works = {}
    for c in chars:
        works.setdefault(c["work"], []).append(c["name"])
    dups = {w: ns for w, ns in works.items() if len(ns) > 1}
    if dups:
        warns.append("同作品多人: " + "; ".join(f"{w}={ns}" for w, ns in dups.items()))

    first = ""
    # --- 卡 JSON ---
    if not CARD.is_file():
        errs.append("缺 圣堂初遇.json")
    else:
        card = json.loads(CARD.read_text(encoding="utf-8"))
        first = card.get("first_mes") or card["data"].get("first_mes") or ""
        entries = card["data"]["character_book"]["entries"]
        comments = [e.get("comment") for e in entries]
        for need in ("世界观", "净化与污秽", "写作与人设规则", "数值影响", "[initvar]变量初始化勿开", "变量列表"):
            if need not in comments:
                errs.append(f"卡内世界书缺: {need}")
        # 写作条不得塞 MVU 格式（知识库：格式在变量输出格式）
        for e in entries:
            if e.get("comment") == "写作与人设规则":
                ct = e.get("content") or ""
                if "<UpdateVariable>" in ct or "JSONPatch" in ct or "变量路径" in ct:
                    errs.append("「写作与人设规则」含变量输出格式，应挪到 [mvu_update]变量输出格式/更新规则")
                if e.get("position") != "at_depth" or e.get("depth") != 0:
                    errs.append("「写作与人设规则」应为 D0（at_depth depth=0）指导条")
            if e.get("comment") == "变量列表":
                ct = e.get("content") or ""
                if "<status_current_variables>" not in ct:
                    errs.append("变量列表标签应为 <status_current_variables>（知识库固定格式）")
                if e.get("position") != "at_depth" or e.get("depth") != 0:
                    errs.append("变量列表应为 at_depth depth=0")
            if str(e.get("comment") or "").startswith("角色_"):
                if e.get("position") != "after_char":
                    errs.append(f"{e.get('comment')} 多角色详细信息应 after_char，现为 {e.get('position')}")
                if e.get("constant"):
                    errs.append(f"{e.get('comment')} 应为绿灯 selective")
            ext = e.get("extensions") or {}
            if not ext.get("exclude_recursion") or not ext.get("prevent_recursion"):
                errs.append(f"{e.get('comment')}: 递归两项未齐（exclude+prevent）")
                break  # 避免 61 条刷屏
        else:
            oks.append("世界书递归选项已齐")
        role_entries = [e for e in entries if str(e.get("comment") or "").startswith("角色_")]
        if len(role_entries) != len(chars):
            errs.append(f"角色绿灯条目 {len(role_entries)} ≠ yaml {len(chars)}")
        else:
            oks.append(f"角色绿灯 {len(role_entries)} 条对齐")
        for e in role_entries:
            if e.get("constant"):
                errs.append(f"{e.get('comment')} 应为 selective 绿灯")
            if not e.get("keys"):
                errs.append(f"{e.get('comment')} 缺 keys")
            if not e.get("constant") and e.get("scan_depth") != 4:
                errs.append(f"{e.get('comment')} scan_depth={e.get('scan_depth')}，本卡应为 4")
        for e in role_entries:
            ct = e.get("content") or ""
            for required in ("演绎锚点:", "口吻:", "不可违背:"):
                if required not in ct:
                    errs.append(f"{e.get('comment')}: 缺人设锚点「{required}」")
        write_e = next((e for e in entries if e.get("comment") == "写作与人设规则"), None)
        if write_e:
            wt = write_e.get("content") or ""
            for required in (
                "人设优先级",
                "防 OOC",
                "防媚{{user}}",
                "不默认赞同{{user}}",
                "关系变化必须有可指认事件",
                "高信任只降低戒备",
            ):
                if required not in wt:
                    errs.append(f"写作与人设规则缺「{required}」")
        schema = ""
        for s in card["data"]["extensions"]["tavern_helper"]["scripts"]:
            if s.get("name") == "变量结构":
                schema = s.get("content") or ""
        for key in (
            "出场角色",
            "角色",
            "好感度",
            "堕落值",
            "依存度",
            "污秽度",
            "信任",
            "当前目标",
            "对user判断",
            "当前边界",
        ):
            if key not in schema:
                errs.append(f"卡内 schema 缺 {key}")
        if "registerMvuSchema" in schema:
            oks.append("MVU schema 已注入")
        schema_source = (ROOT / "plot/schema.mvu.js").read_text(encoding="utf-8")
        if schema != schema_source:
            errs.append("卡内变量结构与 plot/schema.mvu.js 不一致，需重建卡片")
        elif re.findall(r"const\s+(\w+)\s*=\s*z\b", schema) != ["Schema"]:
            errs.append("MVU schema 存在根结构外的 Zod 子 schema，不符合知识库约束")
        else:
            oks.append("卡内 MVU schema 与源码一致且结构内聚")
        for marker in (
            "出场角色: z.preprocess(value => value == null ? [] : value",
            "角色: z.preprocess(",
            "世界: z.preprocess(",
            "主角: z.preprocess(",
            "初遇: z.preprocess(",
        ):
            if marker not in schema:
                errs.append(f"MVU schema 缺空复合值兼容: {marker.split(':', 1)[0]}")
        if ".filter(name => !!data.角色[name])" in schema:
            errs.append("MVU schema 会在角色档案增量写入前误删出场角色")
        else:
            oks.append("MVU schema 保留增量写入中的出场角色")
        if "shengtang/ui/cover" not in first:
            errs.append("first_mes 未指向 shengtang cover CDN")
        else:
            oks.append("封面 CDN 壳已写入 first_mes")
        ok_status = False
        for rs in card["data"]["extensions"].get("regex_scripts") or []:
            if "shengtang/ui/status" in (rs.get("replaceString") or ""):
                ok_status = True
                break
        if not ok_status:
            errs.append("正则状态栏未指向 shengtang/ui/status")
        else:
            oks.append("状态栏 CDN 壳已写入正则")

    # --- 前端文件 ---
    for rel in (
        "src/shengtang/ui/cover/index.html",
        "src/shengtang/ui/status/index.html",
    ):
        p = ROOT / rel
        if not p.is_file():
            errs.append(f"缺文件 {rel}")
        elif p.stat().st_size < 1000:
            warns.append(f"{rel} 过小 ({p.stat().st_size})")
    cover = (ROOT / "src/shengtang/ui/cover/index.html").read_text(encoding="utf-8")
    if "const CHARACTERS = [" not in cover or len(chars) > 0 and chars[0]["name"] not in cover:
        # after sync should embed
        if "牧濑红莉栖" not in cover and "雪之下雪乃" not in cover:
            errs.append("封面 HTML 未同步角色数据（缺人名）")
        else:
            oks.append("封面已内嵌角色数据")
    else:
        oks.append("封面已内嵌角色数据")
    if cover.count('"id":') < len(chars):
        # rough count
        n_id = cover.count('\n    "id":')
        if n_id < len(chars) - 2:
            warns.append(f"封面内嵌 id 约 {n_id}，yaml={len(chars)}")

    # --- 开局事务 / 布局硬伤 ---
    opening_requirements = {
        "generation_id": "generation_id:" in cover,
        "停止生成": "stopGenerationById" in cover,
        "事务提交": bool(re.search(r"message_id:\s*0,\s*message:[\s\S]{0,160}data:", cover)),
        "最终MVU解析": "Mvu.parseMessage(text, initializedData)" in cover,
        "卸载取消": "pagehide" in cover and "stopOpening" in cover,
    }
    for label, passed in opening_requirements.items():
        if passed:
            oks.append(f"开局事务：{label}")
        else:
            errs.append(f"开局事务缺：{label}")
    role_insert = cover.find('{ op: "insert", path: rolePath')
    present_replace = cover.find('{ op: "replace", path: "/世界/出场角色"')
    if role_insert >= 0 and present_replace >= 0 and role_insert < present_replace:
        oks.append("开局先创建角色档案，再写入出场数组")
    else:
        errs.append("开局补丁顺序错误：必须先创建角色档案，再写入出场数组")
    for forbidden in ("deleteExtraFloors", 'getApi("deleteChatMessages")', 'refresh: "all"', "createChatMessages"):
        if forbidden in cover:
            errs.append(f"开局残留危险逻辑: {forbidden}")
    if "should_silence: true" in cover or "should_silence:true" in cover:
        warns.append("开局使用 should_silence:true（知识库：仅影响停止按钮；开局一般应允许停止）")
    if "generateFn({" not in cover and "generate({" not in cover:
        errs.append("封面缺少 generate(...) 调用")
    else:
        if "user_input:" in cover and "should_stream" in cover:
            oks.append("封面 generate 含 user_input + should_stream")
        else:
            warns.append("封面 generate 参数不完整（缺 user_input 或 should_stream）")
    if "十国" in cover and "真理" not in cover and "不以" not in cover:
        warns.append("封面注释仍把十国当权威来源")
    if "scrollbar-width" not in cover and "::-webkit-scrollbar" not in cover:
        errs.append("封面未定制滚动条（易露出系统白粗条）")
    if re.search(r"\.char-grid\s*\{[^}]*max-height:\s*min\([^}]*overflow:\s*auto", cover, re.S):
        errs.append("角色池 char-grid 自带 max-height+overflow（双层滚动，底栏易裁切卡片）")
    if ".page-body" in cover and "scrollbar-color" in cover:
        oks.append("page-body 滚动条已主题化")

    status_html = (ROOT / "src/shengtang/ui/status/index.html").read_text(encoding="utf-8")
    c2_error_count = len(errs)
    for token in ("--st-btn-bg", "--st-btn-edge", "--st-btn-shadow", "--st-btn-active-shadow"):
        if token not in cover or token not in status_html:
            errs.append(f"封面与状态栏缺 C2 共享材质 token: {token}")
    for marker in (":hover", ":active", ":focus-visible", ":disabled"):
        if f".btn{marker}" not in cover:
            errs.append(f"封面按钮缺交互状态: {marker}")
    for selector in (".icon-btn", ".command-btn", ".role-chip"):
        for marker in (":hover", ":active", ":focus-visible", ":disabled"):
            if f"{selector}{marker}" not in status_html:
                errs.append(f"状态栏 {selector} 缺交互状态: {marker}")
    for surface_name, surface in (("封面", cover), ("状态栏", status_html)):
        for marker in ("@media (max-width: 760px)", "@media (max-width: 480px)", "@container"):
            if marker not in surface:
                errs.append(f"{surface_name}缺响应式规则: {marker}")
    for forbidden in (
        "正在初始化变量并请求模型生成",
        "变量已初始化，正在写作首段剧情",
        "正在解析 MVU 变量并替换封面楼层",
        "0 楼已替换为生成结果",
    ):
        if forbidden in cover:
            errs.append(f"封面暴露内部过程文案: {forbidden}")
    if len(errs) == c2_error_count:
        oks.append("封面与状态栏 C2 材质、按钮状态和响应式规则已齐")
    if "setInterval(" in status_html:
        errs.append("状态栏仍使用永久轮询")
    elif "VARIABLE_UPDATE_ENDED" in status_html and "pagehide" in status_html and ".stop()" in status_html:
        oks.append("状态栏事件驱动且可卸载")
    else:
        errs.append("状态栏生命周期不完整")
    for marker in ("Mvu.getMvuData", "getCurrentMessageId", "waitUntil", "getRoleState", "jsonPointerSegment"):
        if marker not in status_html:
            errs.append(f"状态栏缺消息级 MVU/多角色安全逻辑: {marker}")
    if "getAllVariables" in status_html:
        errs.append("状态栏误读 getAllVariables，必须读取所在消息楼层 MVU 数据")
    if re.search(r"`角色\.\$\{", status_html):
        errs.append("状态栏使用点路径读取角色，带点姓名会失效")
    status_regex = next(
        (x for x in card["data"]["extensions"].get("regex_scripts", []) if x.get("scriptName") == "显示-状态栏美化"),
        {},
    )
    status_shell = status_regex.get("replaceString") or ""
    if "overflow:visible" in status_shell and "aspect-ratio:16/10" not in status_shell:
        oks.append("状态栏 CDN 壳由内容撑高")
    else:
        errs.append("状态栏 CDN 壳仍可能按固定比例裁切")

    extensions_blob = json.dumps(card["data"].get("extensions") or {}, ensure_ascii=False)
    for marker in ("大魏芳华", "__mnx", "mnx-", "dist/dawei", "十国千娇"):
        if marker in extensions_blob:
            errs.append(f"卡内模板污染: {marker}")

    # --- git / CDN ---
    code, status = run(["git", "status", "--porcelain", "--untracked-files=no"])
    code2, ahead = run(["git", "rev-list", "--count", "origin/main..HEAD"])
    code3, head = run(["git", "rev-parse", "HEAD"])
    head = head.strip()
    cdn_ref_match = re.search(
        r"custom_begining@([^/]+)/dist/shengtang/ui", first if CARD.is_file() else ""
    )
    cdn_ref = cdn_ref_match.group(1) if cdn_ref_match else "main"
    # 固定 commit 的卡不依赖随后可能被 CI 覆盖的 main 分支内容。
    if cdn_ref != "main":
        code4, _ = run([
            "git", "cat-file", "-e",
            f"{cdn_ref}:dist/shengtang/ui/cover/index.html",
        ])
        if code4:
            errs.append(f"卡内固定 CDN commit 缺封面文件: {cdn_ref}")
        else:
            oks.append(f"固定 CDN commit 已有 dist/shengtang: {cdn_ref[:10]}")
            for kind in ("cover", "status"):
                rel = f"dist/shengtang/ui/{kind}/index.html"
                source = (ROOT / f"src/shengtang/ui/{kind}/index.html").read_text(encoding="utf-8")
                code5, pinned = run_raw(["git", "show", f"{cdn_ref}:{rel}"])
                if code5 or pinned.replace("\r\n", "\n") != source.replace("\r\n", "\n"):
                    errs.append(f"卡内固定 CDN 的 {kind} 与当前源码不一致，需重新固定发布提交")
    else:
        code4, remote_ls = run(["git", "ls-tree", "-r", "origin/main", "--name-only"])
        if "dist/shengtang/ui/cover/index.html" not in remote_ls:
            errs.append("origin/main 无 dist/shengtang → 当前 CDN 链接 404/不可用")
        else:
            oks.append("origin/main 已有 dist/shengtang")
    if status.strip() or (code2 == 0 and int(ahead.strip() or "0") > 0):
        warns.append("本地有已跟踪改动或未推送提交，发布状态需重新核对")
    oks.append(f"本地 HEAD={head[:10]}")

    # CDN URL from build output / card
    m = re.search(r"https://testingcf\.jsdelivr\.net/gh/[^`'\"\s]+shengtang/ui", first if CARD.is_file() else "")
    if m:
        oks.append(f"卡内 CDN 前缀: {m.group(0)}")

    # report
    print("=" * 60)
    print("圣堂初遇 Superpower 审查报告")
    print("=" * 60)
    for x in oks:
        print(f"[OK] {x}")
    for x in warns:
        print(f"[WARN] {x}")
    for x in errs:
        print(f"[ERR] {x}")
    print("-" * 60)
    print(f"合计: OK={len(oks)} WARN={len(warns)} ERR={len(errs)}")
    ready = not errs
    print("整卡就绪:", "否（见 ERR）" if not ready else "是（结构与固定 CDN 均通过）")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
