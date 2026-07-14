# -*- coding: utf-8 -*-
"""《圣堂初遇》阻断式回归检查。"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COVER = (ROOT / "src/shengtang/ui/cover/index.html").read_text(encoding="utf-8")
STATUS = (ROOT / "src/shengtang/ui/status/index.html").read_text(encoding="utf-8")
BUILD = (ROOT / "build_shengtang_card.py").read_text(encoding="utf-8")
CARD = json.loads((ROOT / "圣堂初遇.json").read_text(encoding="utf-8"))
CHARS = yaml.safe_load((ROOT / "plot/characters.yaml").read_text(encoding="utf-8"))["characters"]
WRITE_RULES = (ROOT / "worldbook/02_写作与人设规则.md").read_text(encoding="utf-8")
MVU_RULES = (ROOT / "plot/mvu_update.yaml").read_text(encoding="utf-8")
MVU_SCHEMA = (ROOT / "plot/schema.mvu.js").read_text(encoding="utf-8")
INITVAR = yaml.safe_load((ROOT / "plot/initvar.yaml").read_text(encoding="utf-8"))
WRITING_RULES = WRITE_RULES


class OpeningLifecycleTests(unittest.TestCase):
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
        start = COVER.index("async function startGame()")
        generation = COVER.index("generateFn(", start)
        before_generation = COVER[start:generation]
        self.assertNotIn("replaceMvuData", before_generation)
        self.assertIn("Mvu.parseMessage", COVER[generation:])


class StatusLifecycleTests(unittest.TestCase):
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
    def test_schema_has_present_role_array_and_role_record(self) -> None:
        self.assertIn("z.array(z.string())", MVU_SCHEMA)
        self.assertIn("z.record(z.string(), RoleState)", MVU_SCHEMA)
        self.assertEqual(INITVAR["世界"]["出场角色"], [])
        self.assertEqual(INITVAR["角色"], {})

    def test_schema_normalizes_null_compound_values_from_mvu_initialization(self) -> None:
        self.assertIn(
            "出场角色: z.preprocess(value => value == null ? [] : value",
            MVU_SCHEMA,
        )
        self.assertIn(
            "角色: z.preprocess(value => value == null ? {} : value",
            MVU_SCHEMA,
        )

    def test_schema_migrates_and_normalizes_legacy_state(self) -> None:
        for marker in (
            "同场角色",
            "初遇",
            "new Set",
            "delete data.初遇",
            "delete data.世界.同场角色",
        ):
            self.assertIn(marker, MVU_SCHEMA)

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
            'aria-label="全部角色"',
        ):
            self.assertIn(marker, STATUS)


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


class BuildIsolationTests(unittest.TestCase):
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
                "显示-状态栏排序",
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
    def test_writing_rules_ban_flattery_shortcuts(self) -> None:
        rules = (ROOT / "worldbook/02_写作与人设规则.md").read_text(encoding="utf-8")
        for marker in ("防媚{{user}}", "只有你理解我", "好厉害", "删掉后仍像该角色吗", "万能美人"):
            self.assertIn(marker, rules)

    def test_numeric_rules_do_not_force_obedience(self) -> None:
        numeric = (ROOT / "worldbook/03_数值影响.md").read_text(encoding="utf-8")
        self.assertIn("不是无脑服从", numeric)
        self.assertIn("自动吹捧、讨好或秒信", numeric)
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
        for marker in ("不围着讨好{{user}}转", "禁止捷径吹捧", "无依据则不更新", "秒信/奉承"):
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
        for rule in ("不默认赞同{{user}}", "关系变化必须有可指认事件", "本轮至少让她作出一个"):
            self.assertIn(rule, writing_rules)

    def test_anti_user_flattery_is_enforced_at_all_prompt_layers(self) -> None:
        for marker in (
            "不是围着{{user}}运转的奖励装置",
            "不默认赞同{{user}}",
            "{{user}}不自动替代原作重要关系",
            "关系变化必须有可指认事件",
            "反媚不等于强行敌视",
            "写前暗检",
        ):
            self.assertIn(marker, WRITE_RULES)
        for marker in ("禁止整段围着讨好转", "不得跳到崇拜/献身/秒信", "禁捷径词"):
            self.assertIn(marker, BUILD)
        for marker in ("不奉承、不秒信、不自动把{{user}}当特殊人物", "不等于可爱、可信或值得献身"):
            self.assertIn(marker, COVER)

    def test_relationship_updates_require_evidence_and_small_steps(self) -> None:
        self.assertIn("禁止每回合惯性上涨", MVU_RULES)
        self.assertIn("单次通常不超过 ±2", MVU_RULES)
        self.assertIn("不得仅凭数值跨档自动升级关系称呼", MVU_RULES)
        self.assertIn("不得为了奖励{{user}}而同时上调多项关系数值", MVU_RULES)

    def test_every_generated_profile_preserves_agency(self) -> None:
        missing: list[str] = []
        for char in CHARS:
            path = ROOT / "worldbook/角色" / f"{char['name']}.md"
            if not path.is_file():
                missing.append(f"{char['name']}: 缺生成档案")
                continue
            text = path.read_text(encoding="utf-8")
            for marker in (
                "保留原作核心关系与独立目标",
                "不奉承{{user}}",
                "关系变化必须对应已发生事件",
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
            "角色有独立目标",
            "不默认赞同{{user}}",
            "{{user}}不自动替代原作重要关系",
            "不得凭空赋予{{user}}魅力",
            "关系变化必须有可指认事件",
        ):
            self.assertIn(marker, WRITING_RULES)
        self.assertIn("禁止每回合惯性上涨", MVU_RULES)
        self.assertIn("当前心态不能只围绕{{user}}", MVU_RULES)

    def test_profiles_include_independent_motivation_anchor(self) -> None:
        self.assertIn("行动驱力:", BUILD)
        self.assertIn("原作核心关系", BUILD)
        self.assertIn("不奉承、不秒信、不自动把{{user}}当特殊人物", COVER)


if __name__ == "__main__":
    unittest.main(verbosity=2)
