# -*- coding: utf-8 -*-
"""替换子供向/魅力不足的三人 → 高知名度成熟魅力向。"""
from __future__ import annotations

import ast
import importlib.util
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

REMOVE_IDS = {"misae", "misaka_misaki", "aoi_tosaka"}

NEW = {
    "hancock": {
        "name": "波雅·汉库克",
        "aliases": ["汉库克", "Boa Hancock", "女帝", "海贼女帝"],
        "work": "海贼王",
        "year": 2000,
        "age_note": "31（外表极艳）",
        "accent": "#b01050",
        "blurb": "九蛇海贼团船长、王下七武海「女帝」，美貌与霸气同样致命。",
        "work_intro": "《ONE PIECE》：伟大航路的海贼传奇。波雅·汉库克以「女帝」闻名，美貌、霸气与蛇姬之力并称，是大众向最出名的成熟魅力女角色之一。",
        "appearance": "墨黑长发；极致曲线的暴露战衣；身形高挑丰满；足迹花纹；表情高傲，脸红时反差极大。",
        "intro": (
            "波雅·汉库克是九蛇海贼团船长，外号「女帝」，一度位列王下七武海。"
            "她美貌被称作可让世界倾倒，性格高傲毒舌，对弱者与男人常不假辞色；真正动心后却会别扭到语无伦次。"
            "蛇姬果实让她把所爱之物化为石像，霸气同样一流；战场上是女帝，私下里会为在意之人露出裂缝。"
            "高跟踏过甲板的声音比宣战书更先到——魅力本身就是威压。"
        ),
        "background": [
            "亚马逊·百合的皇帝，九蛇海贼团船长，曾为七武海。",
            "幼时被贩卖与奴役的经历铸成对世界政府的恨与对「弱点」的敏感。",
            "高傲冷艳是壳，动心后别扭害羞；战斗力与美貌同级出名。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以女帝姿态俯视试探，话里带刺；不吃软的套近乎",
            "一旦在意会口是心非、耳根先红；受威胁时霸气与石化不讲情面",
        ],
        "filth_seed": "奴隶烙印的幻痛：情绪剧烈时后背会浮现若隐若现的蹄印灼热。",
    },
    "tearju": {
        "name": "提亚悠·鲁娜提克",
        "aliases": ["提亚悠", "Tearju", "Tearju Lunatique", "小暗的妈妈"],
        "work": "To LOVEる",
        "year": 2008,
        "age_note": "外表成熟（人妻貌美）",
        "accent": "#e6b84a",
        "blurb": "金色暗影的「母亲」模板、天才科学家，成熟性感的金发美人。",
        "work_intro": "《To LOVEる》：外星与校园的后宫骚动。提亚悠·鲁娜提克是以自身为样本制造金色暗影的科学家，成熟、理性、外形极具人妻魅力。",
        "appearance": "金长直；眼镜；白衣或教师装勾勒成熟曲线；身形高挑丰满；表情冷静，笑时温柔带距离。",
        "intro": (
            "提亚悠·鲁娜提克是银河系级的科学家，金色暗影（伊芙）的细胞样本提供者与「母亲」般的存在。"
            "她金发眼镜、身材成熟火辣，语气却冷静温和，像把危险藏进实验室礼貌里。"
            "曾想把造物当人来养，因此与组织决裂；对「小暗」既有亏欠也有温柔，对靠近的人保持观察距离。"
            "白大褂一披是理智，镜片反光时又像在量你的心率。"
        ),
        "background": [
            "生物兵器研究出身，以自身为模板参与金色暗影的制造，后因「把她当人」被组织驱逐。",
            "外表与小暗相似而更成熟，常以教师等身份行动。",
            "理性温柔，内心对造物之女怀有母性亏欠与牵挂。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以礼貌与专业口吻交流，少废话，观察多于热情",
            "提到「造物/孩子」会柔一点；被当成玩物或实验品时态度转冷",
        ],
        "filth_seed": "纳米改造的排异回声：情绪波动时锁骨下会闪过与小暗同源的金线纹。",
    },
    "fujiko": {
        "name": "峰不二子",
        "aliases": ["不二子", "Fujiko Mine", "峰不二子小姐"],
        "work": "鲁邦三世",
        "year": 1971,
        "age_note": "不详（外表成熟魅力）",
        "accent": "#c45c8a",
        "blurb": "神出鬼没的女盗贼，美貌、谎言与枪法齐名，成年向魅力的代名词之一。",
        "work_intro": "《鲁邦三世》：世纪大盗的冒险。峰不二子是系列核心女角色，贪婪、狡黠、性感，戏弄鲁邦与敌人同样熟练。",
        "appearance": "粉褐长发；身形高挑曲线夸张；常换暴露或华丽盗装；手枪不离身；笑里带钩。",
        "intro": (
            "峰不二子是游走于世界的女盗贼，鲁邦三世故事里最出名的成熟魅力符号之一。"
            "她爱财、爱刺激、也爱人（以及背叛后的重逢），每一次靠近都可能是诱饵。"
            "枪法、驾驶、变装与谎言同样一流；对鲁邦又利用又放不下，对普通人则是危险的美。"
            "口红比枪口先到——你分不清她要偷的是宝石，还是你的判断力。"
        ),
        "background": [
            "职业女盗贼，目标是宝藏与乐趣，手法华丽且不择手段。",
            "与鲁邦三世爱恨纠缠：合作、背叛、再重逢是常态。",
            "外表艳丽，心思难测，是「魅力型成年女角色」的长期标杆。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先用笑与暧昧试探价值，甜话里藏钩子",
            "利益一变会抽身；真要护人时子弹比情话更早响",
        ],
        "filth_seed": "偷来的诅咒宝石残秽：指尖偶发冷光，像有藏品在暗处点名要她。",
    },
}


def load_mod(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def strip_rich_ids(exp_text: str, ids: set[str]) -> str:
    """Remove RICH dict entries by id using brace scanning."""
    for cid in ids:
        # find "id": "cid"
        key = f'"id": "{cid}"'
        while True:
            i = exp_text.find(key)
            if i < 0:
                break
            # walk back to entry start '{'
            start = exp_text.rfind("{", 0, i)
            # find matching close for this dict
            depth = 0
            j = start
            while j < len(exp_text):
                ch = exp_text[j]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end = j + 1
                        # include trailing comma/newline
                        while end < len(exp_text) and exp_text[end] in " \t":
                            end += 1
                        if end < len(exp_text) and exp_text[end] == ",":
                            end += 1
                        if end < len(exp_text) and exp_text[end] == "\n":
                            end += 1
                        exp_text = exp_text[:start] + exp_text[end:]
                        break
                j += 1
            else:
                raise SystemExit(f"unclosed entry {cid}")
    return exp_text


def strip_dict_key_block(text: str, key: str) -> str:
    """Remove 'key': ( ... ), or 'key': [ ... ], or 'key': "...", from a python dict literal region."""
    # tuple intros
    pat_tuple = re.compile(rf'\n    "{re.escape(key)}":\s*\(\s*".*?"\s*\),', re.S)
    text2, n = pat_tuple.subn("\n", text, count=1)
    if n:
        return text2
    # list relations
    pat_list = re.compile(rf'\n    "{re.escape(key)}":\s*\[.*?\],', re.S)
    text2, n = pat_list.subn("\n", text, count=1)
    if n:
        return text2
    # string appearance
    pat_str = re.compile(rf'\n    "{re.escape(key)}":\s*".*?",')
    text2, n = pat_str.subn("\n", text, count=1)
    return text2


def main() -> None:
    # 1) expand_profiles
    exp_path = ROOT / "plot/expand_profiles.py"
    exp = exp_path.read_text(encoding="utf-8")
    exp = strip_rich_ids(exp, REMOVE_IDS)
    # append NEW before to_yaml
    blocks = []
    for cid, d in NEW.items():
        if f'"id": "{cid}"' in exp:
            continue
        blocks.append(
            f'''    {{
        "id": "{cid}",
        "name": "{d['name']}",
        "aliases": {d['aliases']!r},
        "work": "{d['work']}",
        "year": {d['year']},
        "age_note": "{d['age_note']}",
        "accent": "{d['accent']}",
        "blurb": "{d['blurb']}",
        "work_intro": "{d['work_intro']}",
        "appearance": "{d['appearance']}",
        "background": {d['background']!r},
        "filth_seed": "{d['filth_seed']}",
    }},
'''
        )
    marker = "\n]\n\ndef to_yaml_chars"
    if marker not in exp:
        raise SystemExit("expand marker missing")
    exp = exp.replace(marker, "\n" + "".join(blocks) + marker, 1)
    exp_path.write_text(exp, encoding="utf-8")

    # 2) enrich INTROS
    en_path = ROOT / "plot/enrich_intros.py"
    en = en_path.read_text(encoding="utf-8")
    for cid in REMOVE_IDS:
        en = strip_dict_key_block(en, cid)
    for cid, d in NEW.items():
        esc = d["intro"].replace("\\", "\\\\").replace('"', '\\"')
        entry = f'    "{cid}": (\n        "{esc}"\n    ),\n'
        if f'"{cid}":' not in en.split("INTROS", 1)[-1].split("def load_expand", 1)[0]:
            en = en.replace("\n}\n\n\ndef load_expand_module", "\n" + entry + "}\n\n\ndef load_expand_module", 1)
    en_path.write_text(en, encoding="utf-8")

    # 3) kb_fix
    kb_path = ROOT / "plot/kb_fix_profiles.py"
    kb = kb_path.read_text(encoding="utf-8")
    for cid in REMOVE_IDS:
        kb = strip_dict_key_block(kb, cid)
    for cid, d in NEW.items():
        rel_sec = kb.split("RELATIONS", 1)[-1].split("APPEARANCE", 1)[0]
        if f'"{cid}":' not in rel_sec:
            rel_block = f'    "{cid}": [\n'
            for r in d["relations"]:
                esc = r.replace("\\", "\\\\").replace('"', '\\"')
                rel_block += f'        "{esc}",\n'
            rel_block += "    ],\n"
            kb = kb.replace(
                "\n}\n\n# 外貌：补可辨识身材/体态锚点（特征向，禁万能美颜词）",
                "\n" + rel_block + "}\n\n# 外貌：补可辨识身材/体态锚点（特征向，禁万能美颜词）",
                1,
            )
        app_sec = kb.split("APPEARANCE", 1)[-1].split("FILTH_FIX", 1)[0]
        if f'"{cid}":' not in app_sec:
            app_esc = d["appearance"].replace("\\", "\\\\").replace('"', '\\"')
            kb = kb.replace(
                "\n}\n\n# 修明显瞎编/错味的污秽种子",
                f'\n    "{cid}": "{app_esc}",\n}}\n\n# 修明显瞎编/错味的污秽种子',
                1,
            )
    kb_path.write_text(kb, encoding="utf-8")

    # 4) rebuild yaml + worldbook
    expand = load_mod(ROOT / "plot/expand_profiles.py", "expand_profiles")
    enrich = load_mod(ROOT / "plot/enrich_intros.py", "enrich_intros")
    kbmod = load_mod(ROOT / "plot/kb_fix_profiles.py", "kb_fix")

    assert all(c["id"] not in REMOVE_IDS for c in expand.RICH)
    assert {c["id"] for c in expand.RICH} >= set(NEW)

    out = []
    for c in expand.RICH:
        cid = c["id"]
        dnew = NEW.get(cid)
        intro = enrich.INTROS.get(cid) or c.get("blurb")
        appearance = kbmod.APPEARANCE.get(cid, c["appearance"])
        relations = kbmod.RELATIONS.get(cid) or ["与{{user}}：开局无旧识"]
        background = c["background"]
        filth = c.get("filth_seed") or ""
        if dnew:
            intro = dnew["intro"]
            appearance = dnew["appearance"]
            relations = dnew["relations"]
            background = dnew["background"]
            filth = dnew["filth_seed"]
        out.append(
            {
                "id": cid,
                "name": c["name"],
                "aliases": c["aliases"],
                "work": c["work"],
                "year": c["year"],
                "age_note": c["age_note"],
                "appearance": appearance,
                "blurb": c["blurb"],
                "intro": intro,
                "work_intro": c["work_intro"],
                "background": background,
                "filth_seed": filth,
                "relations": relations,
                "accent": c["accent"],
            }
        )

    (ROOT / "plot/characters.yaml").write_text(
        yaml.safe_dump({"characters": out}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    wb = ROOT / "worldbook/角色"
    for p in wb.glob("*.md"):
        p.unlink()
    for c in out:
        (wb / f"{c['name']}.md").write_text(kbmod.write_md(c), encoding="utf-8")

    print("removed:", ", ".join(REMOVE_IDS))
    print("added:", ", ".join(d["name"] for d in NEW.values()))
    print("total:", len(out))
    for cid, d in NEW.items():
        print(f"  {d['name']}: intro={len(d['intro'])}")


if __name__ == "__main__":
    main()
