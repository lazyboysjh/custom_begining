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
REVIEW = (ROOT / "scripts/superpower_shengtang_review.py").read_text(encoding="utf-8")
CARD = json.loads((ROOT / "圣堂初遇.json").read_text(encoding="utf-8"))
CHARS = load_characters()
WRITE_RULES = (ROOT / "worldbook/02_写作与人设规则.md").read_text(encoding="utf-8")
STYLE_RULES = (ROOT / "worldbook/04_文风规则.md").read_text(encoding="utf-8") if (ROOT / "worldbook/04_文风规则.md").is_file() else ""
MVU_RULES = (ROOT / "plot/mvu_update.yaml").read_text(encoding="utf-8")
MVU_SCHEMA = (ROOT / "plot/schema.mvu.js").read_text(encoding="utf-8")
INITVAR = yaml.safe_load((ROOT / "plot/initvar.yaml").read_text(encoding="utf-8"))
WRITING_RULES = WRITE_RULES


class CharacterCatalogTests(unittest.TestCase):
    def test_card_builder_defaults_to_frontend_publish_ref(self) -> None:
        self.assertIn('["git", "rev-parse", "origin/main"]', BUILD)
        self.assertNotIn('["git", "rev-parse", "HEAD"]', BUILD)

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
            "返回重选",
            "初遇已就绪",
            "带上这个能力~",
            "就按我写的来~",
            "全部随机开演~",
        ):
            self.assertNotIn(obsolete, COVER + STATUS)
        for expected in (
            "开始召唤啦~",
            "随机一个~",
            "那就开始吧~",
            "召唤仪式进行中",
            "新角色入场",
            "推进剧情",
            "再想一下",
            "来客已现身~",
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
            "关系校准",
            "先呈现角色自己的目标与风险判断",
            "评价依据亲历且可验证的具体事实",
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

    def test_ability_presets_are_playable_special_powers(self) -> None:
        titles = {item["title"] for item in self.options.get("ability_presets") or []}
        for title in ("催眠", "常识改写", "记忆编辑", "时间暂停", "规则覆写", "梦境侵入"):
            self.assertIn(title, titles)

    def test_opening_options_have_one_cover_sync_block(self) -> None:
        self.assertEqual(COVER.count("SYNC_BEGIN:OPENING_OPTIONS"), 1)
        self.assertEqual(COVER.count("SYNC_END:OPENING_OPTIONS"), 1)
        self.assertIn("const OPENING_OPTIONS =", COVER)
        self.assertIn("load_opening_options", BUILD)


class OpeningLifecycleTests(unittest.TestCase):
    def test_constant_worldbook_does_not_embed_character_roster(self) -> None:
        self.assertNotIn("def build_character_overview", BUILD)
        self.assertNotIn('"角色速览"', BUILD)

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

    def test_ability_picker_combines_presets_editing_and_real_random_action(self) -> None:
        self.assertNotIn('id="btnRandomStart"', COVER)
        self.assertNotIn('data-ability-mode=', COVER)
        self.assertNotIn('abilityMode:', COVER)
        self.assertIn('id="btnRandomAbility"', COVER)
        self.assertIn('id="abilityCustom"', COVER)
        self.assertIn('<option value="custom">自定义能力</option>', COVER)
        self.assertIn('preset.value = "custom"', COVER)
        self.assertIn("function randomizeAbility()", COVER)
        self.assertIn("syncAbilityFromPreset", COVER)
        self.assertIn("async function startGame()", COVER)
        self.assertIn("sampleOpeningConfig({ randomAbility: false })", COVER)
        self.assertIn("那就开始吧~", COVER)
        self.assertIn("config:", COVER)
        self.assertIn("const revealPromise = startReveal(config)", COVER)

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
            "/世界/_开局配置/时代背景",
            "/世界/_开局配置/故事类型",
            "/世界/_开局配置/故事氛围",
            "/世界/_开局配置/圣堂形态",
            "/世界/_开局配置/世界融入方式",
            "/世界/圣堂名称",
        ):
            self.assertIn(path, COVER)
        for obsolete_path in (
            "/世界/相遇方式",
            "/世界/教会名",
            "/世界/时代背景",
            "/世界/故事类型",
            "/世界/故事氛围",
            "/世界/圣堂形态",
            "/世界/开局摘要",
        ):
            self.assertNotIn(obsolete_path, COVER)

    def test_cover_exposes_all_editable_hero_fields_with_defaults(self) -> None:
        expected = {
            "heroName": "",
            "heroIdentity": "教堂牧师",
            "heroAppearance": "帅气的高中生",
            "heroPersonality": "阴暗好色",
            "heroStyle": "温和耐心，以救人为先",
            "heroThought": "性压抑的高中男生",
        }
        for field_id, value in expected.items():
            self.assertIn(f'id="{field_id}"', COVER)
            if value:
                self.assertIn(value, COVER)
        self.assertIn('id="abilityCustom"', COVER)
        self.assertIn('function inputText(', COVER)

    def test_never_deletes_chat_floors(self) -> None:
        self.assertNotIn("deleteExtraFloors", COVER)
        self.assertNotIn('getApi("deleteChatMessages")', COVER)

    def test_generation_is_isolated_and_cancellable(self) -> None:
        self.assertIn("generation_id:", COVER)
        self.assertRegex(COVER, r"STREAM_TOKEN_RECEIVED_FULLY[\s\S]+generationId")
        self.assertIn("stopGenerationById", COVER)
        self.assertIn("pagehide", COVER)
        self.assertIn("revealFinishTimer", COVER)
        self.assertRegex(COVER, r"clearTimeout\(state\.revealFinishTimer\)")
        self.assertIn("function clearRevealTimers()", COVER)
        self.assertGreaterEqual(COVER.count("clearRevealTimers()"), 4)

    def test_stream_progress_is_throttled_and_reveal_starts_immediately(self) -> None:
        self.assertIn("function scheduleStreamProgress", COVER)
        start = COVER.index("async function startGame(")
        reveal = COVER.index("startReveal(config)", start)
        wait_mvu = COVER.index("await waitMvu(", start)
        self.assertLess(reveal, wait_mvu)

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
    def test_status_renders_only_useful_role_details(self) -> None:
        for marker in ('id="appearance"', 'id="currentState"', 'id="innerThought"'):
            self.assertIn(marker, STATUS)
        for obsolete in (
            'class="opening-context"', 'id="storyType"', 'id="storyAtmosphere"',
            'id="sanctumForm"', 'id="abilitySummary"', 'id="relation"',
            'id="phase"', 'id="mood"', 'id="goal"', 'id="judgement"',
            'id="boundary"', 'id="filthType"',
        ):
            self.assertNotIn(obsolete, STATUS)

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
    def test_role_schema_is_compact_and_includes_user_relationship(self) -> None:
        for field in ("外貌", "当前状态", "心里想法", "与user关系"):
            self.assertIn(field, MVU_SCHEMA)
            self.assertIn(field, MVU_RULES)
        role_schema = MVU_SCHEMA[MVU_SCHEMA.index("角色: z.preprocess("):]
        for field in ("作品", "是否自定义", "当前目标", "对user判断", "当前边界", "仪式阶段"):
            self.assertNotIn(field, role_schema)
        self.assertIn("与user关系: z.string().prefault('陌生')", role_schema)
        self.assertIn('与user关系: "陌生"', COVER)
        self.assertIn('与user关系: "陌生"', STATUS)
        for marker in ("信任: 0", "好感度: 0", "堕落值: 0", "依存度: 0"):
            self.assertIn(marker, COVER)
            self.assertIn(marker, STATUS)

    def test_frontend_rosters_are_compact(self) -> None:
        cover_roster = COVER[COVER.index("SYNC_BEGIN:CHARACTERS"):COVER.index("SYNC_END:CHARACTERS")]
        status_roster = STATUS[STATUS.index("SYNC_BEGIN:ROSTER"):STATUS.index("SYNC_END:ROSTER")]
        for forbidden in ('"intro":', '"background":', '"aliases":', '"age_note":'):
            self.assertNotIn(forbidden, cover_roster)
            self.assertNotIn(forbidden, status_roster)

    def test_schema_and_initvar_use_readonly_opening_context(self) -> None:
        opening = INITVAR["世界"]["_开局配置"]
        for key, initial in (
            ("时代背景", "待生成"),
            ("故事类型", "待生成"),
            ("故事氛围", "待生成"),
            ("圣堂形态", "圣言堂"),
            ("世界融入方式", "待生成"),
        ):
            self.assertIn(f"{key}: z.string().prefault('{initial}')", MVU_SCHEMA)
            self.assertEqual(opening[key], initial)
            self.assertNotIn(key, MVU_RULES)
        self.assertEqual(INITVAR["世界"]["圣堂名称"], "圣言堂")
        self.assertIn("圣堂名称: z.string().prefault('圣言堂')", MVU_SCHEMA)
        for removed in ("相遇方式", "教会名", "时代背景", "故事类型", "故事氛围", "圣堂形态", "开局摘要", "同场角色"):
            self.assertNotIn(removed, {key: None for key in INITVAR["世界"] if key != "_开局配置"})

    def test_schema_has_present_role_array_and_role_record(self) -> None:
        self.assertIn("z.array(z.string())", MVU_SCHEMA)
        self.assertIn("z.record(", MVU_SCHEMA)
        self.assertIn("z.string(),", MVU_SCHEMA)
        self.assertEqual(INITVAR["世界"]["出场角色"], [])
        self.assertEqual(INITVAR["角色"], {})

    def test_schema_normalizes_null_compound_values_from_mvu_initialization(self) -> None:
        self.assertRegex(
            MVU_SCHEMA,
            r"出场角色:\s*z\.preprocess\(\s*value => value == null \? \[\] : value",
        )
        self.assertRegex(
            MVU_SCHEMA,
            r"角色:\s*z\.preprocess\(\s*value => value == null \? \{\} : value",
        )
        for key in ("世界", "主角"):
            self.assertRegex(
                MVU_SCHEMA,
                rf"{key}:\s*z\.preprocess\(\s*value => value == null \? \{{\}} : value",
            )

    def test_schema_defines_no_detached_zod_subschemas(self) -> None:
        self.assertEqual(re.findall(r"const\s+(\w+)\s*=\s*z\b", MVU_SCHEMA), ["Schema"])

    def test_schema_contains_only_new_world_structure(self) -> None:
        for obsolete in ("同场角色", "初遇:", "相遇方式:", "教会名:", "开局摘要:"):
            self.assertNotIn(obsolete, MVU_SCHEMA)
        for marker in ("_开局配置", "世界融入方式", "圣堂名称", "new Set", ".trim()", "filter(Boolean)"):
            self.assertIn(marker, MVU_SCHEMA)

    def test_schema_normalizes_present_names_and_is_idempotent(self) -> None:
        script = r"""
const fs = require('fs');
global.z = require('zod');
global._ = require('lodash');
let source = fs.readFileSync('plot/schema.mvu.js', 'utf8')
  .replace(/^import[^\n]+\n/, '')
  .replace('export const Schema', 'global.Schema')
  .replace(/\n\$\(\(\) => \{[\s\S]*$/, '');
new Function(source)();
const input = {世界: {出场角色: [' 甲 ', '', '甲', '乙']}, 主角: {}, 角色: {}};
const once = Schema.parse(input);
const twice = Schema.parse(once);
process.stdout.write(JSON.stringify({
  names: once.世界.出场角色,
  idempotent: JSON.stringify(once) === JSON.stringify(twice),
}));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["names"], ["甲", "乙"])
        self.assertTrue(payload["idempotent"])

    def test_release_review_matches_new_schema_contract(self) -> None:
        for marker in ('"_开局配置"', '"世界融入方式"', '"圣堂名称"'):
            self.assertIn(marker, REVIEW)
        for obsolete in ('"当前目标"', '"对user判断"', '"当前边界"', '"初遇: z.preprocess("'):
            self.assertNotIn(obsolete, REVIEW)

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
            'id="roleQuick"',
            'id="relationship"',
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
    def test_cover_uses_full_visual_identity_and_author_credit(self) -> None:
        self.assertIn("万界圣堂", COVER)
        self.assertIn("今天谁来忏悔？", COVER)
        self.assertIn("AUTHOR · AME", COVER)
        self.assertIn("e61846de-b855-4950-b543-672c7d714263.png", COVER)
        self.assertIn("20260716184427370.png", STATUS)
        self.assertIn('class="cover-credit"', COVER)

    def test_cover_subpages_continue_the_visual_background(self) -> None:
        self.assertIn('.page:not([data-page="1"])::before', COVER)
        self.assertIn("isolation: isolate", COVER)
        self.assertGreaterEqual(COVER.count("e61846de-b855-4950-b543-672c7d714263.png"), 3)

    def test_cover_subpage_controls_use_warm_smoked_glass(self) -> None:
        self.assertIn('.page:not([data-page="1"]) .panel', COVER)
        self.assertIn("--ability-glass:", COVER)
        self.assertIn('.page[data-page="2"] .ability-random', COVER)
        self.assertIn("saturate(1.32)", COVER)

    def test_ability_page_uses_unframed_aligned_content_spacing(self) -> None:
        self.assertIn('.page[data-page="2"] .page-body', COVER)
        self.assertIn('class="ability-heading"', COVER)
        self.assertIn('.page[data-page="2"] .ability-heading,', COVER)
        self.assertNotIn("OPENING RITUAL", COVER)
        self.assertIn("border-radius: 0", COVER)
        self.assertIn("border: 0", COVER[COVER.index('.page[data-page="2"] .ability-panel'):])
        self.assertIn("padding: 30px 34px 12px", COVER)

    def test_status_texture_preserves_readability_on_light_hosts(self) -> None:
        self.assertIn("20260716184427370.png", STATUS)
        black_gold = STATUS[STATUS.index("/* Black-gold preview") :]
        self.assertIn("rgba(10,10,13,.9)", black_gold)
        self.assertIn("mix-blend-mode: normal", black_gold.split('html[data-status-bg="a"]', 1)[0])
        self.assertIn("opacity: .28", black_gold.split('html[data-status-bg="a"]', 1)[0])
        self.assertIn("backdrop-filter: none", black_gold.split('html[data-status-bg="a"]', 1)[0])
        self.assertIn("background: rgba(8,9,12,.78)", black_gold)
        self.assertNotIn("grayscale(1)", STATUS)
        self.assertIn("@container (max-width: 820px)", black_gold)
        self.assertIn("@container (max-width: 520px)", black_gold)
        self.assertIn("mask-image: none", black_gold)
        self.assertNotIn("background-size: auto 320px", black_gold)

    def test_status_topbar_shows_world_meta_without_action_note(self) -> None:
        for marker in ('class="meta-strip"', 'id="metaStory"', 'id="metaAtmosphere"', 'id="metaAbility"', "renderWorldMeta", "_开局配置", "故事类型", "故事氛围", "能力摘要", "圣堂名称"):
            self.assertIn(marker, STATUS)
        self.assertNotIn('id="metaEra"', STATUS)
        self.assertNotIn('id="drawNote"', STATUS)
        self.assertNotIn("action-note", STATUS[STATUS.index("<footer class=\"actions\">"):STATUS.index("</footer>", STATUS.index("<footer class=\"actions\">"))])

    def test_cover_home_dedupes_english_brand_copy(self) -> None:
        self.assertNotIn("SANCTUM OF MANY WORLDS", COVER)
        self.assertIn("SANCTUM ENCOUNTER", COVER)

    def test_cover_summon_stage_exposes_halo_fx_layer(self) -> None:
        for marker in ('class="summon-fx"', 'class="summon-beam"', 'class="summon-ring"', 'class="summon-dust"', "@keyframes ringPulse", "@keyframes beamPulse"):
            self.assertIn(marker, COVER)
        # 光环必须大于前景卡，否则召唤动画会被卡片挡住
        self.assertIn("width: min(92%, 520px)", COVER)
        self.assertIn("width: min(72%, 300px)", COVER)

    def test_status_exposes_two_adaptive_background_previews(self) -> None:
        self.assertIn("20260716184427370.png", STATUS)
        self.assertGreaterEqual(STATUS.count("20260716184427370.png"), 4)
        self.assertIn('dataset.statusBg = bg', STATUS)
        self.assertIn('html[data-status-bg="a"] .st-shell::before', STATUS)
        self.assertIn('html[data-status-bg="b"] .st-shell::before', STATUS)

    def test_compact_generation_and_status_controls_remain_usable(self) -> None:
        self.assertIn('.page[data-page="4"] .page-body {', COVER)
        self.assertIn('justify-content: flex-start', COVER[COVER.index('.page[data-page="4"] .page-body {'):])
        self.assertIn('.summon-progress { flex: 0 0 auto;', COVER)
        self.assertIn('@media (max-height: 620px)', COVER)
        self.assertIn('grid-template-rows: minmax(210px,auto) auto', COVER)
        self.assertIn('<span>新角色入场</span>', STATUS)
        self.assertIn('white-space: nowrap', STATUS[STATUS.index('/* Compact tavern iframe polish. */'):])

    def test_cover_generation_copy_stays_inside_summoning_theme(self) -> None:
        for expected in ("召唤仪式进行中", "正在召唤，请稍候~", "异界回响正在聚形", "来客已现身~", "初遇已展开，轮到你回应"):
            self.assertIn(expected, COVER)
        for out_of_theme in ("正在摇人", "翻名单", "冒泡", "已经写到", "灵感正在赶来的路上", "人来啦", "舞台搭好"):
            self.assertNotIn(out_of_theme, COVER)

    def test_status_uses_rpg_layout_without_redundant_top_controls(self) -> None:
        for marker in ('class="character-hero"', 'class="rpg-grid"', 'id="relationship"', "与你的关系", "角色属性", "现场记录"):
            self.assertIn(marker, STATUS)
        for obsolete in ('id="sceneMeta"', 'id="btnPrevRole"', 'id="btnNextRole"', 'id="btnRolePicker"', 'id="rolePicker"'):
            self.assertNotIn(obsolete, STATUS)
        self.assertIn("names.map(name =>", STATUS)
        self.assertNotIn("names.slice(0, 6)", STATUS)

    def test_status_actions_are_unambiguous(self) -> None:
        self.assertIn("新角色入场", STATUS)
        self.assertIn("推进剧情", STATUS)
        self.assertIn("friendlyDrawMessage", STATUS)
        self.assertIn("friendlyAdvanceMessage", STATUS)
        self.assertIn("dispatchAction", STATUS)
        self.assertIn("injects:", STATUS)
        self.assertNotIn("dispatchSend(", STATUS)
        self.assertNotIn("再摇一位~", STATUS)
        self.assertNotIn("故事继续走~", STATUS)

    def test_status_action_prompts_stay_hidden_from_user_message(self) -> None:
        self.assertIn("【新角色入场】请让「", STATUS)
        self.assertIn("【推进剧情｜", STATUS)
        self.assertIn("buildEncounterPrompt", STATUS)
        self.assertIn("buildTogetherPrompt", STATUS)
        # 技术提示走 injects，不直接塞进用户可见楼层
        self.assertIn("content: hidden", STATUS)
        draw = STATUS[STATUS.index("function onDrawEncounter"):STATUS.index("async function onTogetherMoment")]
        self.assertIn("friendlyDrawMessage(character)", draw)
        self.assertIn("buildEncounterPrompt(character, currentStat)", draw)
        together = STATUS[STATUS.index("async function onTogetherMoment"):STATUS.index("window.addEventListener(\"pagehide\"")]
        self.assertIn("friendlyAdvanceMessage(scenario)", together)
        self.assertIn("buildTogetherPrompt(currentStat, scenario)", together)

    def test_xi_shi_appearance_is_visual_not_meta_commentary(self) -> None:
        self.assertNotIn("早期文献强调其美", STATUS)
        self.assertNotIn("本卡不用“捧心”", STATUS)
        self.assertNotIn("早期文献强调其美", COVER)
        self.assertIn("乌发如瀑", STATUS)
        self.assertIn("乌发如瀑", COVER)

    def test_cover_and_status_buttons_use_inline_lucide_icons(self) -> None:
        self.assertGreaterEqual(COVER.count('class="ui-icon"'), 5)
        self.assertGreaterEqual(STATUS.count('class="ui-icon"'), 2)
        for marker in ("lucide-arrow-left", "lucide-shuffle", "lucide-sparkles", "lucide-rotate-ccw"):
            self.assertIn(marker, COVER)
        for marker in ("lucide-user-round-plus", "lucide-wand-sparkles"):
            self.assertIn(marker, STATUS)

    def test_cover_reveal_uses_one_fixed_gacha_stage(self) -> None:
        for marker in ('class="summon-stage"', 'class="summon-sigil"', 'class="summon-card"', 'class="summon-progress"'):
            self.assertIn(marker, COVER)
        self.assertEqual(COVER.count('id="revealStage"'), 1)
        self.assertEqual(COVER.count('id="generationMeter"'), 1)
        self.assertIn("summon-resolved", COVER)

    def test_gacha_sweep_animates_composited_properties_only(self) -> None:
        sweep = COVER[COVER.index("@keyframes summonSweep"):COVER.index("@keyframes sigilTurn")]
        self.assertIn("transform:", sweep)
        self.assertNotIn("background-position", sweep)

    def test_status_advance_uses_filtered_random_scenarios(self) -> None:
        self.assertIn("const ADVANCE_SCENARIOS = [", STATUS)
        self.assertEqual(STATUS.count("requiresMultiple: true"), 1)
        self.assertGreaterEqual(STATUS.count("instruction:"), 8)
        self.assertIn("function pickAdvanceScenario(stat)", STATUS)
        self.assertIn("present.length > 1", STATUS)
        self.assertIn("buildTogetherPrompt(currentStat, scenario)", STATUS)

    def test_active_role_chip_uses_soft_rail_instead_of_bright_outline(self) -> None:
        active = STATUS[STATUS.index(".role-chip.active {"):STATUS.index(".role-chip.active::after")]
        self.assertIn("border-color: rgba(255,255,255,.1)", active)
        self.assertIn("bottom: 0", STATUS)

    def test_cover_native_select_options_keep_dark_contrast(self) -> None:
        self.assertIn("color-scheme: dark", COVER)
        self.assertRegex(COVER, r"select\s+option\s*\{[^}]*background:")
        self.assertRegex(COVER, r"select\s+option\s*\{[^}]*color:")

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
    def test_writing_rules_keep_only_required_sections(self) -> None:
        rules = (ROOT / "worldbook/02_写作与人设规则.md").read_text(encoding="utf-8")
        for marker in ("关系校准:", "写前校准（过程留在幕后）:", "净化戏份:"):
            self.assertIn(marker, rules)
        for removed in ("人设优先级", "演绎校准:", "表达校准:", "数值用法:"):
            self.assertNotIn(removed, rules)

    def test_style_entry_preserves_requested_copy_and_depth(self) -> None:
        requested = (
            "以日式轻小说的风格创作正文。",
            "大量创作主角的内心戏。这些内心戏以诙谐幽默、轻松愉快的角度反馈他者言行或吐槽事件。内心戏无需特殊说明是主角内心所想，自然融入故事，无需括号或其他特殊符号包裹。",
            "对白采用口语化短句，多感叹词和语气词，节奏明快",
            "在日常中保持清淡、俏皮的非日常感",
            "严肃性总是被消解，不得使故事过于 压抑/黑暗/沉重",
            "主要采用短段落，内心戏和对白总是另起一行独立成段，偶尔可以省略发言人",
            "对出场的女性角色生动细腻的描写体现其外貌特点和神态等凸显其人物魅力，对其突出魅力部分，如巨乳、白皙长腿等可进行画面特写",
            "若遇到需要表明发言人的情景，使用多样的人称代词，灵活构造对白的引语标签",
        )
        for line in requested:
            self.assertIn(f"- {line}", STYLE_RULES)
        entry = next(item for item in CARD["data"]["character_book"]["entries"] if item["comment"] == "文风规则")
        self.assertTrue(entry["constant"])
        self.assertEqual(entry["position"], "at_depth")
        self.assertEqual(entry["depth"], 0)
        self.assertEqual(entry["insertion_order"], 4)

    def test_worldbook_uses_new_variable_paths_and_full_user_profile(self) -> None:
        worldview = (ROOT / "worldbook/00_世界观.md").read_text(encoding="utf-8")
        self.assertIn("世界._开局配置.圣堂形态", worldview)
        self.assertIn("世界._开局配置.时代背景", worldview)
        self.assertNotIn("世界.圣堂形态", worldview)
        self.assertNotIn("世界.时代背景", worldview)
        user_start = BUILD.index('USER_ENTRY = """')
        user_entry = BUILD[user_start:BUILD.index("# 写卡知识库", user_start)]
        for field in ("姓名", "身份", "年龄外观", "性格倾向", "表面作风", "私下心思", "能力摘要"):
            self.assertIn(field, user_entry)
        self.assertNotIn("默认教堂牧师", user_entry)

    def test_redundant_global_persona_entry_is_removed(self) -> None:
        self.assertNotIn('add(\n        "人设演绎总则"', BUILD)
        self.assertNotIn("PROFILE_RULES =", BUILD)

    def test_numeric_rules_do_not_force_obedience(self) -> None:
        numeric = (ROOT / "worldbook/03_数值影响.md").read_text(encoding="utf-8")
        self.assertIn("仍按角色口吻表达判断与异议", numeric)
        self.assertIn("评价继续依据已发生事件", numeric)
        self.assertNotIn("依从度高", numeric)

    def test_status_impact_copy_does_not_push_obedience(self) -> None:
        for forbidden in ("依从度高", "依赖暗示增强", "优先寻求接触", "决策先问你"):
            self.assertNotIn(forbidden, STATUS)

    def test_opening_prompt_blocks_instant_devotion(self) -> None:
        self.assertIn("认可效果本身，关系仍按事件推进", COVER)
        self.assertIn("特殊感来自连续相处、共同承担和反复验证", COVER)
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
        for field in ("当前状态", "心里想法"):
            self.assertIn(field, schema)
            self.assertIn(field, COVER)
            self.assertIn(field, update_rules)
        for rule in ("评价依据亲历且可验证的具体事实", "关系变化对应明确事件", "本轮至少让她作出一个"):
            self.assertIn(rule, writing_rules)

    def test_anti_user_flattery_is_enforced_at_all_prompt_layers(self) -> None:
        for marker in (
            "角色自己的目标",
            "评价依据亲历且可验证的具体事实",
            "原作重要关系持续影响判断",
            "关系变化对应明确事件",
            "写前校准",
        ):
            self.assertIn(marker, WRITE_RULES)
        for marker in ("评价基于亲历且可验证的事实", "认可效果本身，关系仍按事件推进"):
            self.assertIn(marker, COVER)

    def test_relationship_updates_require_evidence_and_small_steps(self) -> None:
        self.assertIn("数值保持原值", MVU_RULES)
        self.assertIn("单次通常不超过 ±2", MVU_RULES)
        self.assertIn("实际感知到事件", MVU_RULES)
        self.assertIn("每项变化分别对应本回合可观察依据", MVU_RULES)

    def test_every_generated_profile_uses_four_knowledge_base_sections(self) -> None:
        missing: list[str] = []
        required = ("基本信息:", "外貌特征:", "背景设定:", "关系设定:")
        forbidden = ("角色介绍:", "演绎锚点:", "行动驱力:", "口吻:")
        for char in CHARS:
            path = ROOT / "worldbook/角色" / f"{char['name']}.md"
            if not path.is_file():
                missing.append(f"{char['name']}: 缺生成档案")
                continue
            text = path.read_text(encoding="utf-8")
            for marker in required:
                if marker not in text:
                    missing.append(f"{char['name']}: 缺 {marker}")
            for marker in forbidden:
                if marker in text:
                    missing.append(f"{char['name']}: 仍含 {marker}")
        self.assertEqual(missing, [])

    def test_generated_profile_set_matches_roster(self) -> None:
        generated = {path.stem for path in (ROOT / "worldbook/角色").glob("*.md")}
        expected = {char["name"] for char in CHARS}
        self.assertEqual(generated, expected)

    def test_character_worldbook_entries_follow_multirole_activation_rules(self) -> None:
        entries = CARD["data"]["character_book"]["entries"]
        roles = [entry for entry in entries if str(entry.get("comment") or "").startswith("角色_")]
        self.assertEqual(len(roles), 200)
        for entry in roles:
            self.assertFalse(entry["constant"], entry["comment"])
            self.assertTrue(entry["selective"], entry["comment"])
            self.assertEqual(entry["position"], "after_char", entry["comment"])
            self.assertEqual(entry["scan_depth"], 2, entry["comment"])
            self.assertTrue(entry["keys"], entry["comment"])
            self.assertTrue(entry["extensions"]["exclude_recursion"], entry["comment"])
            self.assertTrue(entry["extensions"]["prevent_recursion"], entry["comment"])

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
            "评价依据亲历且可验证的具体事实",
            "原作重要关系持续影响判断",
            "关系变化对应明确事件",
        ):
            self.assertIn(marker, WRITING_RULES)
        self.assertIn("未发生有效事件时数值保持原值", MVU_RULES)
        self.assertIn("基于角色亲历信息与原作性格", MVU_RULES)

    def test_profiles_use_knowledge_base_four_sections(self) -> None:
        for marker in ("基本信息:", "外貌特征:", "背景设定:", "关系设定:"):
            self.assertIn(marker, BUILD)
        for forbidden in ("角色介绍:", "演绎锚点:", "行动驱力:", "口吻:"):
            self.assertNotIn(forbidden, BUILD)
        self.assertIn("评价基于亲历且可验证的事实", COVER)


if __name__ == "__main__":
    unittest.main(verbosity=2)
