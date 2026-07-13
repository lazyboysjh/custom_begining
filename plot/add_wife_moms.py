# -*- coding: utf-8 -*-
"""新增 7 名人妻/妈妈型角色，写入 expand / enrich / kb_fix，并重生 yaml+世界书。"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

# 7 人：人妻或妈妈型，知名原作，开局无旧识
NEW = {
    "misae": {
        "name": "野原美伢",
        "aliases": ["美伢", "Misae", "野原美冴", "美冴"],
        "work": "蜡笔小新",
        "year": 1992,
        "age_note": "29（剧中设定）",
        "accent": "#e87890",
        "blurb": "野原家主妇，家务与吼人齐名，刀子嘴豆腐心的经典妈妈。",
        "work_intro": "《蜡笔小新》：春日部日常喜剧。野原美伢是小新的母亲，人妻主妇形象深入人心，严厉与疼爱并存。",
        "appearance": "茶色短发；围裙常在；身形丰满偏成熟；表情从温柔到暴怒切换极快；手边常有拖鞋。",
        "intro": (
            "野原美伢是春日部野原家的主妇，小新与小葵的母亲，也是动画史上最出名的「人妻妈妈」之一。"
            "她嗓门大、家务狠、对丈夫广志和小新的捣蛋零容忍，骂完却会默默准备晚饭与关心。"
            "刀子嘴豆腐心：面子要撑住，护短却比谁都快；拖鞋出手如电，心软也如电。"
            "邻里面前要体面，家里却是吼完又心疼的标准人妻节奏。"
        ),
        "background": [
            "野原家主妇，育有小新与小葵；日常围着家务、邻居与儿子闯祸转。",
            "对广志花心与懒散极严，对孩子严厉却极护犊；社交里爱面子。",
            "暴怒与温柔切换快，是经典「人妻妈妈」模板的源头之一。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以主妇礼貌接待，察觉失礼或添乱会立刻提高音量",
            "骂归骂，真出事会护人；家务与规矩先于暧昧",
        ],
        "filth_seed": "邻里闲话的污浊余音：情绪激动时耳边会响起重复的八卦声，像有人在评她的家。",
    },
    "misaka_misaki": {
        "name": "御坂美咲",
        "aliases": ["美咲", "Misaki Misaka", "美琴的母亲"],
        "work": "魔法禁书目录",
        "year": 2008,
        "age_note": "外表年轻（人妻）",
        "accent": "#c45c8a",
        "blurb": "御坂美琴的母亲，外表年轻得不像有高中女儿，温柔天然的人妻。",
        "work_intro": "《魔法禁书目录》/超电磁炮：学园都市超能力体系。御坂美咲是美琴的母亲，以「年轻妈妈」外形和天然温柔著称。",
        "appearance": "茶褐波浪中长发；柔和五官；身形高挑丰满；常穿干练连衣裙或旅行装；笑起来像姐姐多过母亲。",
        "intro": (
            "御坂美咲是御坂美琴的母亲，外表年轻到常被误认成美琴的姐姐，属于学园都市相关作里极出名的人妻形象。"
            "她温柔、天然、有点迷糊，却对女儿的任性与傲娇很有办法；说话轻，关心却到位。"
            "旅行与购物时气场像邻家大姐姐；认真谈起家庭时，母亲的稳定感才会露出来。"
        ),
        "background": [
            "御坂美琴之母，与丈夫御坂田妻分居两地式生活，常来学园都市看女儿。",
            "外表极年轻，性格温柔天然，偶尔迷糊，但对女儿心思敏感。",
            "非能力者，却能在家庭层面稳住「超电磁炮」的别扭。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以温和笑容接近，问话像关心晚辈；不轻易起冲突",
            "提到女儿或家庭时会认真起来；被当成「美琴姐姐」会哭笑不得地纠正",
        ],
        "filth_seed": "学园都市电磁残响沾衣：靠近能力相关区域时发梢会轻微静电竖起。",
    },
    "misato": {
        "name": "葛城美里",
        "aliases": ["美里", "Misato", "美里姐"],
        "work": "新世纪福音战士",
        "year": 1995,
        "age_note": "29",
        "accent": "#6b2d5c",
        "blurb": "NERV战术课长，啤酒与红夹克，照顾驾驶员时像不靠谱却认真的监护人。",
        "work_intro": "《新世纪福音战士》：使徒来袭下的人类补完。葛城美里是战术作战司令，酒精、性感与母性般的监护责任缠在一起。",
        "appearance": "紫红长发；红夹克常披；身形高挑胸围突出；啤酒罐与军用通讯器是符号；笑时豪爽，沉默时疲惫。",
        "intro": (
            "葛城美里是NERV战术作战司令，紫发红夹克，啤酒不离手，作战时却冷静得吓人。"
            "她把碇真嗣接到家里，照顾得乱七八糟却真心实意，像不靠谱却放不下的「监护人妈妈」。"
            "表面浪荡吵闹，夜里会独自扛压力；对驾驶员又凶又护，亲密与界限常常打架。"
            "红夹克一甩就能训人，空罐一丢又露出疲倦的成人温度。"
        ),
        "background": [
            "NERV战术课长/作战司令，第二次冲击幸存者相关家庭背景沉重。",
            "饮酒、性感与豪爽是外壳；对驾驶员有监护欲，家务一塌糊涂。",
            "战场指挥精准，私下情感破绽多，亲密关系里既渴望又逃避。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先用玩笑和啤酒拉开距离；认真时话少、指令清楚",
            "对需要照顾的人会硬塞关心；自己的伤口不许随便碰",
        ],
        "filth_seed": "使徒战的精神污染回声：醉意深时会听见像同步率警告的耳鸣。",
    },
    "irisviel": {
        "name": "爱丽丝菲尔·冯·爱因兹贝伦",
        "aliases": ["爱丽丝菲尔", "Irisviel", "莉莉丝", "爱因兹贝伦的人偶"],
        "work": "Fate/Zero",
        "year": 2011,
        "age_note": "外表二十余（人造·人妻/母亲）",
        "accent": "#e8f0f8",
        "blurb": "爱因兹贝伦人形、骑士帝的御主之妻，温柔母亲，圣杯战争中的悲剧核心。",
        "work_intro": "《Fate/Zero》：第四次圣杯战争前传。爱丽丝菲尔是卫宫切嗣之妻、伊莉雅之母，人造人偶却拥有最人类的温柔。",
        "appearance": "银白长发红瞳；身形纤细却线条柔和；冬装白金为主；笑时温软，战斗补给时会显疲惫。",
        "intro": (
            "爱丽丝菲尔·冯·爱因兹贝伦是爱因兹贝伦家制造的人形，卫宫切嗣的妻子，伊莉雅斯菲尔的母亲。"
            "她温柔、好奇人间，把「成为妻子与母亲」学得很认真；红瞳银发，笑起来像刚学会幸福。"
            "圣杯战争里她既是御主侧的支柱，也是悲剧的容器——越像人类，代价越清晰。"
            "她会为平凡的晚餐开心很久，也会在战场上把温柔耗到极限。"
        ),
        "background": [
            "爱因兹贝伦人造人偶，为圣杯战争而生，却与切嗣结婚并育有伊莉雅。",
            "性格温柔、对世界充满好奇；作为母亲与妻子的情感真实而强烈。",
            "身体与圣杯系统绑定，战斗中常承担残酷消耗。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以柔软礼貌接近，问句多、敌意少；把善意当作默认",
            "涉及家人或「人偶/工具」话题时会安静下来，眼神变沉",
        ],
        "filth_seed": "圣杯泥浊的预震：指尖偶发金红纹路，像有什么在体内苏醒。",
    },
    "aoi_tosaka": {
        "name": "远坂葵",
        "aliases": ["葵", "Aoi Tohsaka", "凛与樱的母亲"],
        "work": "Fate/Zero",
        "year": 2011,
        "age_note": "外表三十前后（人妻/母亲）",
        "accent": "#4a5a8a",
        "blurb": "远坂时臣之妻，凛与樱的母亲，温婉贤淑，被命运碾碎的人妻。",
        "work_intro": "《Fate/Zero》：第四次圣杯战争。远坂葵是远坂家主母，温婉克制，承载姐妹分离与婚姻裂痕的悲剧。",
        "appearance": "黑长直优雅盘或披；着物或得体洋装；身形高挑纤柔；表情常含忍让；眼神温而弱。",
        "intro": (
            "远坂葵是远坂时臣的妻子，远坂凛与间桐樱的母亲，旧日本名门太太式的温婉人妻。"
            "她把委屈吞进礼仪里，对女儿的爱很深，却常无力对抗魔术世界的残酷安排。"
            "笑得体、话轻柔；一旦被逼到墙角，崩溃也会来得安静而彻底。"
            "她越想维持体面的家庭，裂痕就越从沉默里长出来。"
        ),
        "background": [
            "远坂家主母，育有凛与樱；后因家族决定与间桐的交易而骨肉分离。",
            "性格温顺克制，习惯以忍耐维持体面，对丈夫既敬又怨。",
            "非一线战斗者，却是圣杯战争家庭悲剧的核心承受者。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "礼仪周全、声音轻；先忍让，少正面冲突",
            "谈到孩子会眼热；被强迫或羞辱时崩溃来得安静",
        ],
        "filth_seed": "被剥夺的「母性契约」反噬：独处时会听见小女孩叫妈妈的幻听。",
    },
    "kushina": {
        "name": "漩涡玖辛奈",
        "aliases": ["玖辛奈", "Kushina", "红辣椒", "九尾人柱力"],
        "work": "火影忍者",
        "year": 2007,
        "age_note": "24（为人母时期）",
        "accent": "#c81e2a",
        "blurb": "漩涡一族、九尾人柱力，鸣人之母，暴脾气与深情并存的人妻妈妈。",
        "work_intro": "《火影忍者》：忍界羁绊与战争。漩涡玖辛奈是鸣人的母亲，红发暴脾气，爱起人来比忍术还烈。",
        "appearance": "火红长发；紫瞳；身形高挑曲线明显；产妇期以前矫健，笑时豪迈；暴怒时气场压人。",
        "intro": (
            "漩涡玖辛奈来自漩涡隐村，是木叶的九尾人柱力，漩涡鸣人的母亲，波风水门的妻子。"
            "她自称「红辣椒」，嗓门与封印术一样出名：骂人狠，护人更狠，爱情与母性都浓烈直球。"
            "外表火热豪爽，骨子里怕孤独；一旦认定家人，会把命和查克拉一起押上去。"
            "红发一扬就像在宣战，笑起来却又能把「家人」两个字喊得很烫。"
        ),
        "background": [
            "漩涡一族后裔，九尾人柱力，与四代火影水门相爱成婚。",
            "性格火爆外向，封印术高强；对鸣人的爱跨越生死。",
            "怕被抛弃的阴影与热烈性格并存，是忍界经典「人妻母亲」形象。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先热络或呛声试探，不喜欢弯弯绕绕；认定自己人后极护短",
            "提到家人或孤独会突然认真；威胁到孩子/伴侣时杀意先到",
        ],
        "filth_seed": "九尾残秽的温床：情绪激动时红发间会掠过橙黑妖气，像有什么在锁链后抓挠。",
    },
    "hinata": {
        "name": "漩涡雏田",
        "aliases": ["雏田", "Hinata", "日向雏田", "鸣人的妻子"],
        "work": "火影忍者",
        "year": 2014,
        "age_note": "成人（为人妻母后）",
        "accent": "#6a7ab8",
        "blurb": "日向家前继承人，鸣人之妻、博人与向日葵之母，温柔坚韧的人妻。",
        "work_intro": "《火影忍者》/《博人传》：雏田从内向姬到人妻母亲，温柔、坚忍，白眼与柔拳并柔情。",
        "appearance": "墨黑短发（婚后）；白眼；身形柔和丰满偏母性；衣装简洁家常或战斗装；笑时怯仍在，站姿却稳。",
        "intro": (
            "漩涡雏田原姓日向，是日向家前继承人，漩涡鸣人的妻子，博人与向日葵的母亲。"
            "她话少、温柔、容易害羞，关键时刻却会用柔拳把决心打出来；爱得安静，守得坚决。"
            "婚后更添母性从容：仍会脸红，但不再只躲在门后——家人受到威胁时，白眼会先睁开。"
            "她把温柔过成日常，把勇气留给必须出手的那一瞬。"
        ),
        "background": [
            "日向分家/宗家纠葛中长大，曾内向自卑，后在鸣人影响下找到勇气。",
            "与鸣人成婚后育有博人、向日葵；柔拳与白眼仍在，性格转为沉稳温柔。",
            "对人妻与母亲的身份认真，护家时可比外表强硬得多。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先低头小声打招呼，礼貌到近乎怯场；熟悉后会默默照顾人",
            "家人被威胁时态度骤然坚定；害羞时双手交叠，眼神却不躲",
        ],
        "filth_seed": "白眼过度开启的残影：疲惫时瞳中会短暂叠出细小咒纹，像有人在窥视查克拉通路。",
    },
}


def load_mod(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    # 1) append to expand_profiles RICH if missing
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
        # insert before closing of RICH list: \n]\n\ndef to_yaml
        marker = "\n]\n\ndef to_yaml_chars"
        if marker not in exp_text:
            raise SystemExit("expand marker not found")
        exp_text = exp_text.replace(marker, "\n" + block + marker, 1)
    exp_path.write_text(exp_text, encoding="utf-8")

    # 2) patch enrich INTROS
    en_path = ROOT / "plot/enrich_intros.py"
    en = en_path.read_text(encoding="utf-8")
    for cid, d in NEW.items():
        if f'"{cid}":' in en and f'"{cid}": (' in en:
            # replace existing
            pat = re.compile(rf'"{re.escape(cid)}":\s*\(\s*".*?"\s*\),', re.S)
            esc = d["intro"].replace("\\", "\\\\").replace('"', '\\"')
            en, n = pat.subn(f'"{cid}": (\n        "{esc}"\n    ),', en, count=1)
            if n:
                continue
        # insert before closing of INTROS
        esc = d["intro"].replace("\\", "\\\\").replace('"', '\\"')
        entry = f'    "{cid}": (\n        "{esc}"\n    ),\n'
        marker = "\n}\n\n\ndef load_expand_module"
        if marker not in en:
            marker = "\n}\n\ndef load_expand_module"
        if marker not in en:
            raise SystemExit("enrich INTROS end not found")
        en = en.replace(marker, "\n" + entry + marker, 1)
    en_path.write_text(en, encoding="utf-8")

    # 3) patch kb_fix RELATIONS + APPEARANCE
    kb_path = ROOT / "plot/kb_fix_profiles.py"
    kb = kb_path.read_text(encoding="utf-8")
    for cid, d in NEW.items():
        if f'"{cid}":' not in kb.split("RELATIONS", 1)[-1].split("APPEARANCE", 1)[0]:
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
        # appearance
        app_esc = d["appearance"].replace("\\", "\\\\").replace('"', '\\"')
        if f'"{cid}":' not in kb.split("APPEARANCE", 1)[-1].split("FILTH_FIX", 1)[0]:
            kb = kb.replace(
                "\n}\n\n# 修明显瞎编/错味的污秽种子",
                f'\n    "{cid}": "{app_esc}",\n}}\n\n# 修明显瞎编/错味的污秽种子',
                1,
            )
    kb_path.write_text(kb, encoding="utf-8")

    # 4) rebuild yaml + worldbook from yaml merge
    expand = load_mod(ROOT / "plot/expand_profiles.py", "expand_profiles")
    enrich = load_mod(ROOT / "plot/enrich_intros.py", "enrich_intros")
    kbmod = load_mod(ROOT / "plot/kb_fix_profiles.py", "kb_fix_profiles")

    old_yaml = {}
    yp = ROOT / "plot/characters.yaml"
    if yp.exists():
        old_yaml = {c["id"]: c for c in yaml.safe_load(yp.read_text(encoding="utf-8"))["characters"]}

    out = []
    for c in expand.RICH:
        cid = c["id"]
        dnew = NEW.get(cid)
        intro = (enrich.INTROS.get(cid) if hasattr(enrich, "INTROS") else None) or (
            dnew["intro"] if dnew else None
        ) or old_yaml.get(cid, {}).get("intro") or c.get("blurb")
        appearance = kbmod.APPEARANCE.get(cid) or (dnew["appearance"] if dnew else c["appearance"])
        relations = kbmod.RELATIONS.get(cid) or (dnew["relations"] if dnew else ["与{{user}}：开局无旧识"])
        background = (dnew["background"] if dnew else None) or c["background"]
        filth = c.get("filth_seed") or (dnew["filth_seed"] if dnew else "")
        if dnew:
            # force NEW fields onto RICH-derived
            appearance = dnew["appearance"]
            background = dnew["background"]
            intro = dnew["intro"]
            relations = dnew["relations"]
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

    print(f"total characters: {len(out)}")
    print("new:", ", ".join(NEW[k]["name"] for k in NEW))
    missing_rel = [c["id"] for c in out if c["id"] not in kbmod.RELATIONS and c["id"] not in NEW]
    if missing_rel:
        print("WARN missing rel in kb:", missing_rel[:10])


if __name__ == "__main__":
    main()
