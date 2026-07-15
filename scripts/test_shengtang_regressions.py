# -*- coding: utf-8 -*-
"""《圣堂初遇》阻断式回归检查。"""
from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path

import yaml

from build_shengtang_card import load_character_sources, load_characters

ROOT = Path(__file__).resolve().parents[1]
COVER = (ROOT / "src/shengtang/ui/cover/index.html").read_text(encoding="utf-8")
STATUS = (ROOT / "src/shengtang/ui/status/index.html").read_text(encoding="utf-8")
BUILD = (ROOT / "build_shengtang_card.py").read_text(encoding="utf-8")
CARD = json.loads((ROOT / "圣堂初遇.json").read_text(encoding="utf-8"))
CHARS = load_characters()
WRITE_RULES = (ROOT / "worldbook/02_写作与人设规则.md").read_text(encoding="utf-8")
MVU_RULES = (ROOT / "plot/mvu_update.yaml").read_text(encoding="utf-8")
MVU_SCHEMA = (ROOT / "plot/schema.mvu.js").read_text(encoding="utf-8")
INITVAR = yaml.safe_load((ROOT / "plot/initvar.yaml").read_text(encoding="utf-8"))
WRITING_RULES = WRITE_RULES


class CharacterCatalogTests(unittest.TestCase):
    def test_roster_has_exactly_200_unique_characters(self) -> None:
        self.assertEqual(len(CHARS), 200)
        self.assertEqual(len({char["id"] for char in CHARS}), 200)
        self.assertEqual(len({char["name"] for char in CHARS}), 200)
        recent = yaml.safe_load(
            (ROOT / "plot/character_batches/recent_anime.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(len(recent["characters"]), 50)
        self.assertEqual(set(recent["sources"]), {char["id"] for char in recent["characters"]})

    def test_revised_ui_copy_is_present_and_obsolete_copy_is_removed(self) -> None:
        for obsolete in (
            "枢纽抽卡",
            "相聚一刻",
            "一键随机开始",
            "生成开局",
            "开始初遇",
            "随机启程",
            "揭晓初遇",
            "召来新客",
            "推进当前幕",
        ):
            self.assertNotIn(obsolete, COVER + STATUS)
        for expected in (
            "开始召唤啦~",
            "命运随便摇~",
            "看看谁来啦",
            "神秘嘉宾加载中",
            "再摇一位~",
            "故事继续走~",
            "看看其他人",
        ):
            self.assertIn(expected, COVER + STATUS)

    def test_core_worldbook_uses_positive_guidance_language(self) -> None:
        core = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in (
                "worldbook/00_世界观.md",
                "worldbook/01_净化与污秽.md",
                "worldbook/02_写作与人设规则.md",
                "worldbook/03_数值影响.md",
                "plot/mvu_update.yaml",
            )
        )
        for directive in ("禁止", "不得", "严禁", "不可违背"):
            self.assertNotIn(directive, core)
        for marker in (
            "演绎校准",
            "先呈现角色自己的目标与风险判断",
            "评价依据亲历且可验证的行为",
            "关系变化对应明确事件",
        ):
            self.assertIn(marker, core)

    def test_new_batches_have_complete_source_records(self) -> None:
        base = yaml.safe_load((ROOT / "plot/characters.yaml").read_text(encoding="utf-8"))["characters"]
        base_ids = {char["id"] for char in base}
        added = [char for char in CHARS if char["id"] not in base_ids]
        sources = load_character_sources()
        self.assertEqual(len(base), 78)
        self.assertEqual(len(added), 122)
        self.assertEqual(set(sources), {char["id"] for char in added})
        for char in added:
            source = sources[char["id"]]
            self.assertTrue(source.get("category"), char["name"])
            self.assertTrue(source.get("primary"), char["name"])
            self.assertTrue(source.get("notes"), char["name"])

    def test_added_profiles_are_individually_complete(self) -> None:
        base_ids = {
            char["id"]
            for char in yaml.safe_load(
                (ROOT / "plot/characters.yaml").read_text(encoding="utf-8")
            )["characters"]
        }
        recent_ids = {
            char["id"]
            for char in yaml.safe_load(
                (ROOT / "plot/character_batches/recent_anime.yaml").read_text(encoding="utf-8")
            )["characters"]
        }
        required_text = ("name", "work", "appearance", "blurb", "intro", "work_intro", "filth_seed")
        for char in (item for item in CHARS if item["id"] not in base_ids):
            for field in required_text:
                self.assertTrue(str(char.get(field) or "").strip(), f"{char['id']}: {field}")
            self.assertGreaterEqual(len(char.get("aliases") or []), 3, char["id"])
            if char["id"] in recent_ids:
                aliases = {
                    str(alias).strip().casefold()
                    for alias in (char.get("aliases") or [])
                    if str(alias).strip()
                }
                self.assertNotIn(char["name"].strip().casefold(), aliases, char["id"])
                self.assertGreaterEqual(len(aliases), 3, char["id"])
            self.assertGreaterEqual(len(char.get("background") or []), 3, char["id"])
            self.assertGreaterEqual(len(char.get("relations") or []), 3, char["id"])
            self.assertEqual(char["relations"][0], "与{{user}}：开局无旧识", char["id"])

    def test_aliases_do_not_collide_across_roster(self) -> None:
        owners: dict[str, str] = {}
        collisions: list[str] = []
        for char in CHARS:
            for raw in [char["name"], *(char.get("aliases") or [])]:
                alias = str(raw).strip().casefold()
                if not alias:
                    continue
                owner = owners.setdefault(alias, char["id"])
                if owner != char["id"]:
                    collisions.append(f"{raw}: {owner} / {char['id']}")
        self.assertEqual(collisions, [])

    def test_real_performers_are_not_random_roleplay_targets(self) -> None:
        roster_text = "\n".join(
            str(alias)
            for char in CHARS
            for alias in [char["name"], *(char.get("aliases") or [])]
        )
        for name in ("杨幂", "刘诗诗", "唐嫣", "刘亦菲", "赵丽颖", "迪丽热巴"):
            self.assertNotIn(name, roster_text)

    def test_generated_profiles_omit_blank_age_fields(self) -> None:
        for char in CHARS:
            profile = (ROOT / "worldbook" / "角色" / f"{char['name']}.md").read_text(encoding="utf-8")
            self.assertNotIn("    年龄: \n", profile, char["name"])


class OpeningOptionTests(unittest.TestCase):
    def setUp(self) -> None:
        path = ROOT / "plot/opening_options.yaml"
        self.assertTrue(path.exists(), "缺 plot/opening_options.yaml")
        self.options = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def test_story_types_are_exactly_thirty_distinct_structures(self) -> None:
        stories = self.options.get("story_types") or []
        self.assertEqual(len(stories), 30)
        self.assertEqual(len({item["id"] for item in stories}), 30)
        self.assertEqual(len({item["title"] for item in stories}), 30)
        for item in stories:
            self.assertTrue(item.get("core_goal"))
            self.assertTrue(item.get("failure_stakes"))
            self.assertTrue(item.get("prompt"))

    def test_opening_dimensions_are_complete(self) -> None:
        self.assertEqual(len(self.options.get("atmospheres") or []), 10)
        for key in (
            "atmospheres",
            "eras",
            "sanctum_forms",
            "integration_modes",
            "ability_presets",
        ):
            values = self.options.get(key) or []
            self.assertGreater(len(values), 0, key)
            self.assertEqual(len({item["id"] for item in values}), len(values), key)

    def test_opening_options_have_one_cover_sync_block(self) -> None:
        self.assertEqual(COVER.count("SYNC_BEGIN:OPENING_OPTIONS"), 1)
        self.assertEqual(COVER.count("SYNC_END:OPENING_OPTIONS"), 1)
        self.assertIn("const OPENING_OPTIONS =", COVER)
        self.assertIn("load_opening_options", BUILD)


class OpeningLifecycleTests(unittest.TestCase):
    def test_cover_samples_all_random_dimensions_without_manual_heroine_picker(self) -> None:
        self.assertNotIn('id="modeGrid"', COVER)
        self.assertNotIn('id="charGrid"', COVER)
        self.assertNotIn('data-tab="pool"', COVER)
        self.assertIn("function sampleOpeningConfig", COVER)
        self.assertIn("function randomIndex", COVER)
        for marker in (
            "OPENING_OPTIONS.story_types",
            "OPENING_OPTIONS.atmospheres",
            "OPENING_OPTIONS.eras",
            "OPENING_OPTIONS.sanctum_forms",
            "OPENING_OPTIONS.integration_modes",
            "CHARACTERS",
        ):
            self.assertIn(marker, COVER)

    def test_normal_and_one_click_random_start_share_locked_config(self) -> None:
        self.assertIn('id="btnRandomStart"', COVER)
        self.assertIn("async function startGame(randomAll = false)", COVER)
        self.assertIn("sampleOpeningConfig({ randomAbility: randomAll })", COVER)
        self.assertIn("config:", COVER)
        self.assertIn("activeOpening.config", COVER)

    def test_cross_era_prompt_requires_complete_causal_chain(self) -> None:
        for marker in (
            "为何出现在当前世界",
            "当前时代的身份",
            "与圣堂发生联系",
            "主动追求",
            "异常如何进入因果链",
            "核心性格",
            "功能相近",
        ):
            self.assertIn(marker, COVER)

    def test_opening_patches_persist_public_random_context(self) -> None:
        for path in (
            "/世界/时代背景",
            "/世界/故事类型",
            "/世界/故事氛围",
            "/世界/圣堂形态",
            "/世界/开局摘要",
        ):
            self.assertIn(path, COVER)

    def test_never_deletes_chat_floors(self) -> None:
        self.assertNotIn("deleteExtraFloors", COVER)
        self.assertNotIn('getApi("deleteChatMessages")', COVER)

    def test_generation_is_isolated_and_cancellable(self) -> None:
        self.assertIn("generation_id:", COVER)
        self.assertRegex(COVER, r"STREAM_TOKEN_RECEIVED_FULLY[\s\S]+generationId")
        self.assertIn("stopGenerationById", COVER)
        self.assertIn("pagehide", COVER)

    def test_stream_does_not_replace_floor_zero(self) -> None:
        listener = re.search(
            r"onStream\s*=\s*\([^)]*\)\s*=>\s*\{([\s\S]*?)\n\s*\};",
            COVER,
        )
        self.assertIsNotNone(listener)
        self.assertNotIn("setMsgs", listener.group(1))
        self.assertNotIn("setChatMessages", listener.group(1))

    def test_final_commit_is_single_transaction(self) -> None:
        self.assertRegex(
            COVER,
            r"setMsgs\(\s*\[\{\s*message_id:\s*0,\s*message:\s*[^,]+,\s*data:",
        )
        self.assertNotIn('refresh: "all"', COVER)
        self.assertNotIn("createChatMessages", COVER)
        self.assertGreaterEqual(COVER.count("assertOpeningCanCommit(run, getMsgs)"), 2)
        commit = COVER.index("await setMsgs(")
        self.assertGreater(COVER.index("activeOpening = null;", commit), commit)

    def test_mvu_is_not_written_before_generation(self) -> None:
        start = COVER.index("async function startGame(")
        generation = COVER.index("generateFn(", start)
        before_generation = COVER[start:generation]
        self.assertNotIn("replaceMvuData", before_generation)
        self.assertIn("Mvu.parseMessage", COVER[generation:])


class StatusLifecycleTests(unittest.TestCase):
    def test_status_renders_public_opening_context_and_ability(self) -> None:
        for marker in (
            'id="storyType"',
            'id="storyAtmosphere"',
            'id="sanctumForm"',
            'id="abilitySummary"',
            "world.故事类型",
            "world.故事氛围",
            "world.圣堂形态",
            "currentStat.主角",
        ):
            self.assertIn(marker, STATUS)
        self.assertNotIn('id="integrationMode"', STATUS)

    def test_status_has_no_render_blocking_font_dependency(self) -> None:
        self.assertNotIn("fonts.googleapis.com", STATUS)
        self.assertNotIn("fonts.gstatic.com", STATUS)

    def test_status_is_event_driven_and_disposable(self) -> None:
        self.assertNotIn("setInterval(", STATUS)
        self.assertIn("VARIABLE_UPDATE_ENDED", STATUS)
        self.assertIn("pagehide", STATUS)
        self.assertRegex(STATUS, r"\.stop\(\)")
        bind_block = STATUS[STATUS.index("async function bind()"):STATUS.index("function toast(")]
        self.assertGreaterEqual(bind_block.count("if (destroyed) return;"), 2)

    def test_status_has_explicit_data_states(self) -> None:
        for marker in ("status-loading", "status-empty", "status-error"):
            self.assertIn(marker, STATUS)

    def test_status_shell_uses_content_height(self) -> None:
        render = next(
            item
            for item in CARD["data"]["extensions"]["regex_scripts"]
            if item["scriptName"] == "显示-状态栏美化"
        )["replaceString"]
        self.assertIn("overflow:visible", render)
        self.assertNotIn("aspect-ratio:16/10", render)


class MultiRoleStateTests(unittest.TestCase):
    def test_schema_and_initvar_include_public_opening_context(self) -> None:
        for key, initial in (
            ("时代背景", "待生成"),
            ("故事类型", "待生成"),
            ("故事氛围", "待生成"),
            ("圣堂形态", "圣言堂"),
            ("开局摘要", "待生成"),
        ):
            self.assertIn(f"{key}: z.string().prefault('{initial}')", MVU_SCHEMA)
            self.assertEqual(INITVAR["世界"][key], initial)
            self.assertIn(key, MVU_RULES)

    def test_schema_has_present_role_array_and_role_record(self) -> None:
        self.assertIn("z.array(z.string())", MVU_SCHEMA)
        self.assertIn("z.record(", MVU_SCHEMA)
        self.assertIn("z.string(),", MVU_SCHEMA)
        self.assertEqual(INITVAR["世界"]["出场角色"], [])
        self.assertEqual(INITVAR["角色"], {})

    def test_schema_normalizes_null_compound_values_from_mvu_initialization(self) -> None:
        self.assertIn(
            "出场角色: z.preprocess(value => value == null ? [] : value",
            MVU_SCHEMA,
        )
        self.assertRegex(
            MVU_SCHEMA,
            r"角色:\s*z\.preprocess\(\s*value => value == null \? \{\} : value",
        )
        for key in ("世界", "主角", "初遇"):
            self.assertRegex(
                MVU_SCHEMA,
                rf"{key}:\s*z\.preprocess\(\s*value => value == null \? \{{\}} : value",
            )

    def test_schema_defines_no_detached_zod_subschemas(self) -> None:
        self.assertEqual(re.findall(r"const\s+(\w+)\s*=\s*z\b", MVU_SCHEMA), ["Schema"])

    def test_schema_migrates_and_normalizes_legacy_state(self) -> None:
        for marker in (
            "同场角色",
            "初遇",
            "new Set",
            "delete data.初遇",
            "delete data.世界.同场角色",
        ):
            self.assertIn(marker, MVU_SCHEMA)

    def test_schema_keeps_present_name_during_incremental_role_creation(self) -> None:
        script = r"""
const fs = require('fs');
global.z = require('zod');
global._ = require('lodash');
let source = fs.readFileSync('plot/schema.mvu.js', 'utf8')
  .replace(/^import[^\n]+\n/, '')
  .replace('export const Schema', 'global.Schema')
  .replace(/\n\$\(\(\) => \{[\s\S]*$/, '');
new Function(source)();
const world = '\u4e16\u754c';
const present = '\u51fa\u573a\u89d2\u8272';
const hero = '\u4e3b\u89d2';
const roles = '\u89d2\u8272';
const first = '\u521d\u9047';
const name = '\u6f29\u6da1\u7396\u8f9b\u5948';
const input = {
  [world]: {[present]: [name]},
  [hero]: {},
  [roles]: {},
  [first]: {},
};
process.stdout.write(JSON.stringify(Schema.parse(input)[world][present]));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(json.loads(result.stdout), ["漩涡玖辛奈"])

    def test_opening_creates_role_before_marking_it_present(self) -> None:
        role_insert = COVER.index('{ op: "insert", path: rolePath')
        present_replace = COVER.index('{ op: "replace", path: "/世界/出场角色"')
        self.assertLess(role_insert, present_replace)

    def test_multirole_rules_keep_character_updates_independent(self) -> None:
        for marker in (
            "出场角色",
            "角色.[姓名]",
            "实际感知",
            "未出场角色",
            "/世界/出场角色/-",
        ):
            self.assertIn(marker, MVU_RULES)

    def test_opening_and_draw_prompts_write_multirole_paths(self) -> None:
        self.assertIn('/世界/出场角色', COVER)
        self.assertIn('/角色/', COVER)
        self.assertIn('/世界/出场角色', STATUS)
        self.assertIn('/角色/', STATUS)
        self.assertNotIn('/世界/同场角色', STATUS)

    def test_status_renders_selected_role_from_current_scene(self) -> None:
        for marker in (
            "stat_data.世界.出场角色",
            "stat_data.角色",
            "activeRoleName",
            "renderRoleSwitcher",
            'id="rolePicker"',
            'aria-label="切换来客"',
        ):
            self.assertIn(marker, STATUS)

    def test_status_reads_current_message_mvu_after_stat_data_exists(self) -> None:
        for marker in (
            "Mvu.getMvuData",
            "getCurrentMessageId",
            "waitUntil",
            "stat_data",
        ):
            self.assertIn(marker, STATUS)
        self.assertNotIn("getAllVariables", STATUS)

    def test_status_uses_literal_role_keys_and_escaped_json_pointers(self) -> None:
        self.assertIn("function getRoleState", STATUS)
        self.assertIn("roles[name]", STATUS)
        self.assertNotIn("`角色.${activeRoleName}`", STATUS)
        self.assertIn("function jsonPointerSegment", STATUS)
        self.assertIn("jsonPointerSegment(character.name)", STATUS)
        self.assertIn("const focusPath = jsonPointerSegment(focus)", STATUS)

    def test_draw_never_readds_a_role_already_in_scene(self) -> None:
        self.assertNotIn("available.length ? available : pool", STATUS)
        self.assertIn("if (!available.length) return null", STATUS)


class ProductUiTests(unittest.TestCase):
    def test_cover_and_status_share_product_tokens(self) -> None:
        for token in (
            "--st-bg",
            "--st-surface",
            "--st-line",
            "--st-gold",
            "--st-radius",
            "--st-ease",
        ):
            self.assertIn(token, COVER)
            self.assertIn(token, STATUS)

    def test_internal_copy_is_not_rendered(self) -> None:
        self.assertNotIn("UI ·", COVER)
        self.assertNotIn("v9 · pc-opening", COVER)
        self.assertNotIn("MVU变量初始化成功", STATUS)
        self.assertNotIn("Ambient orbs", STATUS)

    def test_layout_avoids_viewport_height_and_horizontal_page_scroll(self) -> None:
        self.assertNotRegex(COVER, r"\b\d+(?:\.\d+)?vh\b")
        self.assertNotRegex(STATUS, r"\b\d+(?:\.\d+)?vh\b")
        self.assertIn("overflow-x: hidden", COVER)
        self.assertIn("overflow-x: hidden", STATUS)

    def test_motion_has_reduced_motion_fallback(self) -> None:
        self.assertIn("prefers-reduced-motion: reduce", COVER)
        self.assertIn("prefers-reduced-motion: reduce", STATUS)

    def test_cover_reveal_has_accessible_independent_states(self) -> None:
        for marker in (
            'id="revealStage"',
            'id="revealName"',
            'id="revealWork"',
            'id="revealBlurb"',
            'aria-live="polite"',
            "revealDone",
            "generationDone",
            "function startReveal",
            "function finishReveal",
        ):
            self.assertIn(marker, COVER)

    def test_c2_surfaces_share_material_button_tokens(self) -> None:
        for token in (
            "--st-btn-bg",
            "--st-btn-edge",
            "--st-btn-shadow",
            "--st-btn-active-shadow",
        ):
            self.assertIn(token, COVER)
            self.assertIn(token, STATUS)

    def test_c2_buttons_cover_all_interaction_states(self) -> None:
        for marker in (":hover", ":active", ":focus-visible", ":disabled"):
            self.assertIn(f".btn{marker}", COVER)
        for selector in (".icon-btn", ".command-btn", ".role-chip"):
            for marker in (":hover", ":active", ":focus-visible", ":disabled"):
                self.assertIn(f"{selector}{marker}", STATUS)

    def test_c2_has_phone_tablet_and_desktop_container_rules(self) -> None:
        for surface in (COVER, STATUS):
            self.assertIn("@media (max-width: 760px)", surface)
            self.assertIn("@media (max-width: 480px)", surface)
            self.assertIn("@container", surface)

    def test_generation_copy_does_not_expose_internal_processes(self) -> None:
        for forbidden in (
            "正在初始化变量并请求模型生成",
            "变量已初始化，正在写作首段剧情",
            "正在解析 MVU 变量并替换封面楼层",
            "0 楼已替换为生成结果",
            "MVU 未初始化，请确认变量框架已启用",
        ):
            self.assertNotIn(forbidden, COVER)


class BuildIsolationTests(unittest.TestCase):
    def test_static_copy_script_is_valid_javascript(self) -> None:
        result = subprocess.run(
            ["node", "--check", "scripts/copy_shengtang_static.mjs"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_build_uses_repository_local_template(self) -> None:
        self.assertRegex(BUILD, r'TEMPLATE\s*=\s*ROOT\s*/\s*"templates"\s*/\s*"shengtang_base\.json"')
        self.assertNotIn(r"E:\create\十国千娇", BUILD)
        template = ROOT / "templates/shengtang_base.json"
        self.assertTrue(template.is_file())
        parsed = json.loads(template.read_text(encoding="utf-8"))
        self.assertEqual(parsed.get("spec"), "chara_card_v2")

    def test_card_has_no_foreign_template_runtime(self) -> None:
        blob = json.dumps(CARD["data"]["extensions"], ensure_ascii=False)
        for marker in ("大魏芳华", "[大魏芳华", "__mnx", "mnx-", "dist/dawei", "十国千娇"):
            self.assertNotIn(marker, blob)

    def test_card_does_not_claim_all_characters_are_adults(self) -> None:
        scenario = CARD.get("scenario", "") + CARD["data"].get("scenario", "")
        self.assertNotIn("成年二次元女性", scenario)

    def test_regex_and_helper_scripts_are_whitelisted(self) -> None:
        helper_names = [
            item.get("name")
            for item in CARD["data"]["extensions"].get("tavern_helper", {}).get("scripts", [])
        ]
        self.assertEqual(helper_names, ["变量结构", "MVUbeta"])
        regex_names = [
            item.get("scriptName")
            for item in CARD["data"]["extensions"].get("regex_scripts", [])
        ]
        self.assertEqual(
            regex_names,
            [
                "显示-封面HTML后移除状态栏占位",
                "显示-状态栏美化",
                "显示-隐藏变量更新块",
                "提示词-隐藏状态栏占位",
                "提示词-仅发送近3楼变量",
                "提示词-隐藏界面CDN壳",
            ],
        )


class CharacterSourceTests(unittest.TestCase):
    def test_character_ids_and_names_are_unique(self) -> None:
        ids = [c["id"] for c in CHARS]
        names = [c["name"] for c in CHARS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))

    def test_aliases_do_not_name_other_characters(self) -> None:
        owners = {c["name"]: c["name"] for c in CHARS}
        collisions: list[str] = []
        for char in CHARS:
            for alias in char.get("aliases") or []:
                alias = str(alias).strip()
                other = owners.get(alias)
                if other and other != char["name"]:
                    collisions.append(f"{char['name']} -> {alias} ({other})")
        self.assertEqual(collisions, [])

    def test_zero_two_does_not_claim_ichigo_alias(self) -> None:
        zero_two = next(c for c in CHARS if c["name"] == "零二")
        self.assertNotIn("莓", zero_two.get("aliases") or [])


class AntiSycophancyTests(unittest.TestCase):
    def test_writing_rules_guide_evidence_based_relationships(self) -> None:
        rules = (ROOT / "worldbook/02_写作与人设规则.md").read_text(encoding="utf-8")
        for marker in ("关系校准", "具体事实", "明确事件", "角色自己的目标", "可辨识特征"):
            self.assertIn(marker, rules)

    def test_numeric_rules_do_not_force_obedience(self) -> None:
        numeric = (ROOT / "worldbook/03_数值影响.md").read_text(encoding="utf-8")
        self.assertIn("仍按角色口吻表达判断与异议", numeric)
        self.assertIn("评价继续依据已发生事件", numeric)
        self.assertNotIn("依从度高", numeric)

    def test_status_impact_copy_does_not_push_obedience(self) -> None:
        for forbidden in ("依从度高", "依赖暗示增强", "优先寻求接触", "决策先问你"):
            self.assertNotIn(forbidden, STATUS)

    def test_opening_prompt_blocks_instant_devotion(self) -> None:
        self.assertIn("不等于可爱、可信或值得献身", COVER)
        self.assertIn("只有你", COVER)
        self.assertIn("openingGoal(", COVER)
        self.assertNotIn("clipVoice(enc.背景 || enc.简介, 72)", COVER)

    def test_status_action_prompts_block_flattery(self) -> None:
        for marker in ("先处理自己的目标", "评价基于可验证事实", "关系变化对应本轮事件"):
            self.assertIn(marker, STATUS)

    def test_anti_sycophancy_state_is_persistent(self) -> None:
        schema = next(
            item["content"]
            for item in CARD["data"]["extensions"]["tavern_helper"]["scripts"]
            if item["name"] == "变量结构"
        )
        update_rules = (ROOT / "plot/mvu_update.yaml").read_text(encoding="utf-8")
        writing_rules = (ROOT / "worldbook/02_写作与人设规则.md").read_text(encoding="utf-8")
        for field in ("当前目标", "对user判断", "当前边界"):
            self.assertIn(field, schema)
            self.assertIn(field, COVER)
            self.assertIn(field, update_rules)
        for rule in ("评价依据亲历且可验证的行为", "关系变化对应明确事件", "本轮至少让她作出一个"):
            self.assertIn(rule, writing_rules)

    def test_anti_user_flattery_is_enforced_at_all_prompt_layers(self) -> None:
        for marker in (
            "角色自己的目标",
            "评价依据亲历且可验证的行为",
            "原作重要关系持续影响判断",
            "关系变化对应明确事件",
            "认可具体事实",
            "写前校准",
        ):
            self.assertIn(marker, WRITE_RULES)
        for marker in ("先呈现角色自己的目标与风险判断", "认可净化效果本身", "特殊感来自连续事件"):
            self.assertIn(marker, BUILD)
        for marker in ("评价基于亲历且可验证的事实", "认可效果本身，关系仍按事件推进"):
            self.assertIn(marker, COVER)

    def test_relationship_updates_require_evidence_and_small_steps(self) -> None:
        self.assertIn("数值保持原值", MVU_RULES)
        self.assertIn("单次通常不超过 ±2", MVU_RULES)
        self.assertIn("关系称呼只随实际关系事件调整", MVU_RULES)
        self.assertIn("每项变化分别对应本回合可观察依据", MVU_RULES)

    def test_every_generated_profile_preserves_agency(self) -> None:
        missing: list[str] = []
        for char in CHARS:
            path = ROOT / "worldbook/角色" / f"{char['name']}.md"
            if not path.is_file():
                missing.append(f"{char['name']}: 缺生成档案")
                continue
            text = path.read_text(encoding="utf-8")
            for marker in (
                "演绎锚点",
                "原作核心关系与独立目标持续影响选择",
                "对{{user}}的评价依据亲历且可验证的事实",
                "关系变化对应已发生事件",
            ):
                if marker not in text:
                    missing.append(f"{char['name']}: {marker}")
        self.assertEqual(missing, [])

    def test_generated_profile_set_matches_roster(self) -> None:
        generated = {path.stem for path in (ROOT / "worldbook/角色").glob("*.md")}
        expected = {char["name"] for char in CHARS}
        self.assertEqual(generated, expected)

    def test_known_canon_crossovers_are_removed(self) -> None:
        source = (ROOT / "plot/characters.yaml").read_text(encoding="utf-8")
        for marker in (
            "兄长大树",
            "拉妲希雅·福特·马库斯·艾尔文",
            "世界级道具「埃癸斯之盾」",
            "继承「瞬神」之名",
            "不愿被故乡库洛里艾绑住",
            "桐子本名小一",
            "甲贺朧",
            "朧是甲贺",
            "EVA二号机驾驶员",
            "与碇源堂：听命关系",
            "与绫濑桃：姑母",
            "育有圆与小女儿",
            "日向分家/宗家纠葛",
            "霞诗姐」出道",
            "与义妹间桐樱",
            "远坂凛是次女当主",
            "对魔物解剖与食用有学术级热情",
            "演艺世家与偶像经历",
            "appearance: 黑长直；黑白对比装",
            "出身东京浅草花街",
            "艾丝妲妮雅·尤·艾拉利亚",
            "国立半藏学院忍教师",
            "蛇姬果实",
        ):
            self.assertNotIn(marker, source)

    def test_rules_block_user_fawning(self) -> None:
        for marker in (
            "角色自己的目标",
            "评价依据亲历且可验证的行为",
            "原作重要关系持续影响判断",
            "认可具体事实",
            "关系变化对应明确事件",
        ):
            self.assertIn(marker, WRITING_RULES)
        self.assertIn("未发生有效事件时数值保持原值", MVU_RULES)
        self.assertIn("当前心态同时保留角色自身目标", MVU_RULES)

    def test_profiles_include_independent_motivation_anchor(self) -> None:
        self.assertIn("行动驱力:", BUILD)
        self.assertIn("原作核心关系", BUILD)
        self.assertIn("评价基于亲历且可验证的事实", COVER)


if __name__ == "__main__":
    unittest.main(verbosity=2)
