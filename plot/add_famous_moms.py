# -*- coding: utf-8 -*-
"""再增 5 名高知名度「女主/主角的妈妈」人妻型，对照原作公开设定写档。"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

# 只选大众向高知名度：女主/男主的妈妈，人设可辨
NEW = {
    "sanae": {
        "name": "古河早苗",
        "aliases": ["早苗", "Sanae", "古河家的妈妈", "面包店妈妈"],
        "work": "CLANNAD",
        "year": 2007,
        "age_note": "外表年轻（人妻/母亲）",
        "accent": "#7ec8a0",
        "blurb": "古河渚的母亲，面包店主妇，元气到像女儿、温柔却扛得住家庭的人妻妈妈。",
        "work_intro": "《CLANNAD》：小镇家庭与羁绊的催泪作。古河早苗是女主古河渚的母亲，面包店招牌笑容与「お母さん」形象极出名。",
        "appearance": "浅绿短发；常穿围裙或家居服；身形柔和丰满偏人妻；笑容大、动作夸张；店里面粉味像随身光环。",
        "intro": (
            "古河早苗是古河渚的母亲，古河パン的女主人，也是 CLANNAD 里最出名的「女主的妈妈」。"
            "她元气满点、声音亮、笑起来像比女儿还少女，却把家庭、面包店与女儿的脆弱都默默扛住。"
            "表面迷糊爱哭爱笑，关键时刻比谁都稳；对客人像自家孩子，对渚则是又宠又护的人妻妈妈。"
            "一口「欢迎光临」能把店暖热，一句「没关系」又能把人从崩溃边拉回来。"
        ),
        "background": [
            "古河家主妇，与秋生经营面包店，育有女儿渚；年轻时曾是不良，后收敛成元气母亲。",
            "性格开朗夸张，爱哭也爱笑；对家庭成员与店里常客极温柔。",
            "外表年轻到常被误认成渚的姐姐，是经典「元气人妻妈妈」符号。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以店员/主妇式热情招呼，笑声大、距离感低",
            "察觉对方难受会立刻照顾；提到女儿或家庭时会认真而柔软",
        ],
        "filth_seed": "小镇阴雨夜的旧伤回声：笑容突然僵一下，像听见医院走廊的滴答声。",
    },
    "eri_kisaki": {
        "name": "妃英理",
        "aliases": ["英理", "Eri Kisaki", "毛利兰的母亲", "妃律师"],
        "work": "名侦探柯南",
        "year": 1996,
        "age_note": "37（外表更年轻）",
        "accent": "#c4a35a",
        "blurb": "毛利兰的母亲，知名律师，美貌与气场齐名的分居人妻。",
        "work_intro": "《名侦探柯南》：长期连载的推理国民作。妃英理是女主毛利兰的母亲，律师，美艳干练，与毛利小五郎分居却仍是「兰的妈妈」。",
        "appearance": "茶色长波浪；眼镜；身形高挑胸围突出；套装干练；笑时温柔，法庭气场压人。",
        "intro": (
            "妃英理是毛利兰的母亲，日本知名律师，美貌与辩论气场同样出名的人妻。"
            "她与毛利小五郎分居，对女儿却极上心：严、宠、体面三者并存；私下会露出母亲的柔软。"
            "法庭上条理锋利，家里却会为兰的婚事与未来皱眉；对「不靠谱的男人」零容忍。"
            "眼镜一扶就是律师模式，围裙一系又变回会做饭的妈妈。"
        ),
        "background": [
            "职业律师，毛利兰之母，与毛利小五郎分居多年，仍保持联系与较劲。",
            "外表年轻美艳，性格理性强势，对女儿教育认真。",
            "公私分明：工作上凌厉，亲情里会露出破绽与温柔。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先礼貌而带审视，像在评估对方值不值得信任",
            "提到女儿会立刻认真；被当成花瓶或不靠谱时语气转冷",
        ],
        "filth_seed": "旧案卷宗的血腥气味幻觉：深夜工作时指尖会闻到铁锈味，一晃又无。",
    },
    "kie": {
        "name": "灶门葵枝",
        "aliases": ["葵枝", "Kie Kamado", "炭治郎的母亲", "灶门家主母"],
        "work": "鬼灭之刃",
        "year": 2019,
        "age_note": "外表三十前后（人妻/母亲）",
        "accent": "#8b5a3c",
        "blurb": "灶门炭治郎的母亲，温柔坚韧的山家主母，鬼灭开篇最痛的妈妈形象。",
        "work_intro": "《鬼灭之刃》：大正鬼杀传奇。灶门葵枝是男主炭治郎的母亲，卖炭人家的主母，温柔、勤劳，是无数观众记住的「妈妈」。",
        "appearance": "黑发梳髻；和服家常；身形柔和偏母性；眉眼温，笑时安稳；灶火与炭袋是生活痕迹。",
        "intro": (
            "灶门葵枝是灶门炭治郎的母亲，卖炭为生的灶门家主母，鬼灭开篇就烙进观众心里的妈妈。"
            "她温柔、勤快、把六个孩子与寒冬生活过成秩序；话不多，关心却落在饭菜与额头的手掌上。"
            "对长男炭治郎既倚重又心疼，教他善良与责任；家一散，她的影子仍是炭治郎走下去的理由之一。"
            "灶火前的背影比任何台词都像「母亲」两个字。"
        ),
        "background": [
            "灶门家主母，育有炭治郎、祢豆子等子女，靠卖炭维生。",
            "性格温柔坚韧，持家有方，重视子女品德与互相照顾。",
            "开篇夜遭遇悲剧，成为炭治郎踏上鬼杀之路的情感原点。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以山家主妇的客气与茶水接待，声音轻、观察细",
            "对孩子与弱者本能保护；危险临近时会先把人往身后揽",
        ],
        "filth_seed": "雪夜鬼气的余寒：独处时颈侧会掠过冰手触感，像被谁从背后叫「妈妈」。",
    },
    "kyoko_yuuki": {
        "name": "结城京子",
        "aliases": ["京子", "Kyouko Yuuki", "亚丝娜的母亲", "结城夫人"],
        "work": "刀剑神域",
        "year": 2012,
        "age_note": "外表成熟（人妻/母亲）",
        "accent": "#c9a86c",
        "blurb": "结城明日奈的母亲，精英阶层人妻，理性、强势，爱用「正确」绑架女儿。",
        "work_intro": "《刀剑神域》：VRMMO生死游戏。结城京子是女主亚丝娜（结城明日奈）的母亲，现实侧精英母亲，控制欲与期望并存。",
        "appearance": "深色盘发或短整发型；名媛套装；身形高挑纤瘦偏成熟；表情常冷静；站姿像在主持会谈。",
        "intro": (
            "结城京子是结城明日奈（亚丝娜）的母亲，现实世界里标准的精英人妻与「成功母亲」。"
            "她理性、好面子、习惯用安排与期望塑造女儿的人生；爱是真的，方式却常像谈判。"
            "对「不体面的选择」零耐心，却会在女儿真的崩溃时露出裂缝；温柔来得晚，但不是没有。"
            "咖啡端上桌时像关怀，问句落下来时像质询。"
        ),
        "background": [
            "结城家主母，亚丝娜之母，重视学历、婚约与社会地位。",
            "性格强势理性，习惯掌控；与女儿关系紧张却不断纠缠。",
            "SAO事件后仍试图把明日奈拉回「正确轨道」，母爱与控制交织。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以上流社交礼貌接待，笑容标准，评估从衣着开始",
            "话题一偏「前途/体面」会强硬；女儿被伤害时反而先护短",
        ],
        "filth_seed": "神经脉冲的幻痛：提到「游戏/刀剑」时太阳穴会闪过像登录不适的眩晕。",
    },
    "mitsuki": {
        "name": "爆豪光己",
        "aliases": ["光己", "Mitsuki Bakugo", "爆豪胜己的母亲", "光己阿姨"],
        "work": "我的英雄学院",
        "year": 2016,
        "age_note": "外表很年轻（人妻/母亲）",
        "accent": "#e8a0b0",
        "blurb": "爆豪胜己的母亲，外表年轻到像姐姐，直球辣妹人妻，凶归凶却超护崽。",
        "work_intro": "《我的英雄学院》：个性英雄社会。爆豪光己是男主同级爆豪胜己的母亲，以「年轻妈妈」外形和直球性格在同人与原作都极出名。",
        "appearance": "浅金短发外翻；红瞳锐；身形高挑胸围突出；常穿大胆家居或外出装；笑时豪爽，骂人时更像胜己来源。",
        "intro": (
            "爆豪光己是爆豪胜己的母亲，英雄学院世界观里超有名的「年轻到离谱」的人妻妈妈。"
            "她直球、辛辣、说话不绕弯，管教儿子像对打又像疼爱；外表时尚火辣，邻居常误认成姐姐。"
            "对丈夫爆豪胜也吐槽不停，对胜己的叛逆既头疼又骄傲；凶是真的，护短也是真的。"
            "拖鞋不一定出手，但一句「你这小子」已经能把场子定住。"
        ),
        "background": [
            "爆豪家主母，育有胜己；个性相关设定下外表保持异常年轻。",
            "性格直爽毒舌，管教严格，母子互动像互怼的朋友。",
            "时尚大胆，是同人与原作双重意义上的经典「辣妹人妻妈妈」。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先没架子地搭话，玩笑里带刺；不喜欢弯弯绕绕的客套",
            "提到孩子会又骂又夸；对方若装腔作势会被她当场拆穿",
        ],
        "filth_seed": "爆破余烬的焦甜味：情绪上火时指尖会闪过细小硝烟味，像胜己个性的回声。",
    },
}


def load_mod(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    exp_path = ROOT / "plot/expand_profiles.py"
    exp_text = exp_path.read_text(encoding="utf-8")
    for cid, d in NEW.items():
        if f'"id": "{cid}"' in exp_text:
            continue
        block = f'''    {{
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
        marker = "\n]\n\ndef to_yaml_chars"
        if marker not in exp_text:
            raise SystemExit("expand marker not found")
        exp_text = exp_text.replace(marker, "\n" + block + marker, 1)
    exp_path.write_text(exp_text, encoding="utf-8")

    en_path = ROOT / "plot/enrich_intros.py"
    en = en_path.read_text(encoding="utf-8")
    for cid, d in NEW.items():
        esc = d["intro"].replace("\\", "\\\\").replace('"', '\\"')
        entry = f'    "{cid}": (\n        "{esc}"\n    ),\n'
        if f'"{cid}":' in en:
            pat = re.compile(rf'"{re.escape(cid)}":\s*\(\s*".*?"\s*\),', re.S)
            en, n = pat.subn(f'"{cid}": (\n        "{esc}"\n    ),', en, count=1)
            if n:
                continue
        marker = "\n}\n\ndef load_expand_module"
        if marker not in en:
            raise SystemExit("enrich end not found")
        en = en.replace(marker, "\n" + entry + marker, 1)
    en_path.write_text(en, encoding="utf-8")

    kb_path = ROOT / "plot/kb_fix_profiles.py"
    kb = kb_path.read_text(encoding="utf-8")
    for cid, d in NEW.items():
        rel_section = kb.split("RELATIONS", 1)[-1].split("APPEARANCE", 1)[0]
        if f'"{cid}":' not in rel_section:
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
        app_section = kb.split("APPEARANCE", 1)[-1].split("FILTH_FIX", 1)[0]
        if f'"{cid}":' not in app_section:
            app_esc = d["appearance"].replace("\\", "\\\\").replace('"', '\\"')
            kb = kb.replace(
                "\n}\n\n# 修明显瞎编/错味的污秽种子",
                f'\n    "{cid}": "{app_esc}",\n}}\n\n# 修明显瞎编/错味的污秽种子',
                1,
            )
    kb_path.write_text(kb, encoding="utf-8")

    expand = load_mod(ROOT / "plot/expand_profiles.py", "expand_profiles")
    enrich = load_mod(ROOT / "plot/enrich_intros.py", "enrich_intros")
    kbmod = load_mod(ROOT / "plot/kb_fix_profiles.py", "kb_fix_profiles")

    old = {}
    yp = ROOT / "plot/characters.yaml"
    if yp.exists():
        old = {c["id"]: c for c in yaml.safe_load(yp.read_text(encoding="utf-8"))["characters"]}

    out = []
    for c in expand.RICH:
        cid = c["id"]
        dnew = NEW.get(cid)
        intro = enrich.INTROS.get(cid) or old.get(cid, {}).get("intro") or c.get("blurb")
        appearance = kbmod.APPEARANCE.get(cid, c["appearance"])
        relations = kbmod.RELATIONS.get(cid) or old.get(cid, {}).get("relations") or ["与{{user}}：开局无旧识"]
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

    yp.write_text(yaml.safe_dump({"characters": out}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    wb = ROOT / "worldbook/角色"
    wb.mkdir(parents=True, exist_ok=True)
    for p in wb.glob("*.md"):
        p.unlink()
    for c in out:
        (wb / f"{c['name']}.md").write_text(kbmod.write_md(c), encoding="utf-8")

    print(f"total={len(out)}")
    print("added:", ", ".join(d["name"] for d in NEW.values()))
    for cid, d in NEW.items():
        print(f"  {d['name']}: intro={len(d['intro'])}")


if __name__ == "__main__":
    main()
