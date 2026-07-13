# -*- coding: utf-8 -*-
"""新增 5 名高知名度「性感温柔妈妈系」（不限年代）。"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

NEW = {
    "raikou": {
        "name": "源赖光",
        "aliases": ["赖光", "Raikou", "源赖光〔Berserker〕", "妈妈赖光"],
        "work": "Fate/Grand Order",
        "year": 2015,
        "age_note": "不详（英灵·成熟母性）",
        "accent": "#6b4c9a",
        "blurb": "平安传奇的鬼削者，却以压倒性母性与成熟色气著称的「妈妈」英灵。",
        "work_intro": "《Fate/Grand Order》：英灵召唤的手游现象级作品。源赖光在玩家社群里几乎成了「性感温柔妈妈」代名词，战斗力与溺爱同级出名。",
        "appearance": "紫黑长发；巨乳窄腰的暴露铠饰；身形高挑丰满；金睛或柔光；笑时溺爱，怒时威压如鬼。",
        "intro": (
            "源赖光是平安京传说中的鬼之削者，在 Fate 里却以「妈妈」人格爆红：成熟、性感、温柔到溺爱。"
            "她把在意的人当孩子般呵护，嗓音软、拥抱紧，占有欲却藏在母性笑容里。"
            "战场上是斩鬼的狂战士，日常里会为饭菜与穿衣操心；色气自然，不靠刻意勾引。"
            "一句「妈妈来了」比任何技能名都先传开——温柔与危险是同一具身体。"
        ),
        "background": [
            "以源氏武者为基底的英灵，斩鬼传说与「母性暴走」并存。",
            "对眷属/孩子般的对象极度保护，温柔体贴，越界时也以关爱为名。",
            "外形成熟性感，是同人与正式演出双重意义上的妈妈系符号。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以柔声关心接近，递茶递食物，距离感低得像家里人",
            "受威胁时母性转杀意；被拒绝关心会受伤但仍不放手",
        ],
        "filth_seed": "鬼血余烬：溺爱过深时瞳色会闪过非人金芒，像有什么在叫「孩子」。",
    },
    "tamamo": {
        "name": "玉藻前",
        "aliases": ["玉藻", "Tamamo", "玉藻の前", "狐狸小姐"],
        "work": "Fate/EXTRA",
        "year": 2010,
        "age_note": "不详（妖狐·人妻貌）",
        "accent": "#e87830",
        "blurb": "自称良好人妻的妖狐，娇媚温柔，尾巴里藏着深情与危险。",
        "work_intro": "《Fate/EXTRA》及 FGO：玉藻前以「良好人妻」自居，娇声、色气与忠诚绑在一起，是人气长期居高的性感温柔系。",
        "appearance": "浅粉金发；狐耳多尾；巫女改装偏暴露；身形娇柔有料；笑时眯眼，尾巴会先泄情绪。",
        "intro": (
            "玉藻前是流传千年的妖狐，Fate 里最出名的「自称良好人妻」之一：娇、媚、温柔，服务精神拉满。"
            "她喜欢被需要，会做饭、会撒娇、会把主人奉到中心；色气来自亲昵，而不是冰冷的炫耀。"
            "真心一旦押上就深得可怕，被抛弃的阴影让温柔里带刺；尾巴摇起来时，你分不清是爱还是咒。"
            "「玉藻会努力当好妻子」——这句话本身就是武器。"
        ),
        "background": [
            "以妲己传说为影子的狐之英灵，渴望被爱与「人妻」身份认同。",
            "性格娇俏温柔，擅长侍奉与魅惑，对契约对象极度专一。",
            "战斗时可展神威，日常却像黏人的狐妻。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以娇声与服务靠近，自称人妻候选人也不害羞",
            "被认真对待会更黏；被当玩物会笑着收尾巴，眼里却冷",
        ],
        "filth_seed": "神镜裂痕的狐火：情动时耳尖飘蓝白狐火，像旧神在低声索取供奉。",
    },
    "ransheya": {
        "name": "拉歇希亚·戴比路克",
        "aliases": ["拉歇希亚", "戴比路克女王", "Ranchea", "拉拉的母亲"],
        "work": "To LOVEる",
        "year": 2008,
        "age_note": "外表成熟（女王/母亲）",
        "accent": "#d45c9a",
        "blurb": "戴比路克星女王，拉拉之母，丰满性感却对家人异常温柔。",
        "work_intro": "《To LOVEる》：银河系王族与地球的闹剧。拉歇希亚是女主拉拉的母亲、戴比路克女王，以成熟色气与母性同时出名。",
        "appearance": "粉系长发；皇冠与暴露王袍；身形极丰满成熟；气质慵懒温柔；笑时像把银河当客厅。",
        "intro": (
            "拉歇希亚·戴比路克是戴比路克星女王，拉拉·萨塔琳·戴比路克的母亲，系列里最直白的性感温柔妈妈。"
            "她身材与气场都是「女王级」，说话却软、笑起来宠，对女儿和在意之人毫不吝啬体温。"
            "政治与毁灭力都可怕，回家却能变成会撒娇的母亲；色气是天性，温柔是选择。"
            "披风一掀是王权，伸手摸摸头时又只是妈妈。"
        ),
        "background": [
            "戴比路克星统治者，与国王育有拉拉等女儿，战斗力深不可测。",
            "性格温和宠溺，外形却极度性感成熟。",
            "对家庭成员纵容又骄傲，是典型的「性感女王妈妈」。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以懒洋洋的女王礼节接待，笑意多、压迫感却在",
            "对诚恳的人会突然很亲昵；伤害女儿时女王面具瞬间冷掉",
        ],
        "filth_seed": "毁灭种族的血脉躁动：拥抱过紧时皮肤下会闪过粉金纹路，像星球在共鸣。",
    },
    "ryoko": {
        "name": "御门凉子",
        "aliases": ["凉子", "Ryoko", "御门老师", "凉子老师"],
        "work": "To LOVEる",
        "year": 2008,
        "age_note": "外表成熟（人妻型）",
        "accent": "#c45c6a",
        "blurb": "彩南高中教师，成熟丰满的黑发美人，温柔里带着人妻色气。",
        "work_intro": "《To LOVEる》：校园与外星公主。御门凉子是常驻的成熟女性角色，教师身份、温柔谈吐与性感体态并存，人妻感极强。",
        "appearance": "黑长直；眼镜常挂；胸围突出的教师装/毛衣；身形成熟丰满；笑时温柔，弯腰时杀伤力先到。",
        "intro": (
            "御门凉子是彩南高中的教师，To LOVEる里最稳的「性感温柔人妻型」常驻角色之一。"
            "她对学生温和负责，嗓音稳，笑起来让人放松；身材却大胆得像故意考验心跳。"
            "不靠娇蛮抢戏，色气来自成熟与体贴；被卷进骚动时也常先护人，再无奈扶镜框。"
            "讲台上是凉子老师，靠近时又像会把热可可塞进你手里的邻居姐姐兼人妻。"
        ),
        "background": [
            "彩南高中教师，常被卷进拉拉一行的混乱却保持成人风度。",
            "性格温柔可靠，少见暴走，是校园侧的成熟女性象征。",
            "外形丰满性感，与温和性格形成经典反差。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以教师/成人礼貌接待，语气软、界线清晰",
            "对方为难会先帮；被过分轻薄会笑着警告，仍不撕破脸",
        ],
        "filth_seed": "外星骚动的余波：独自批改时耳边会闪过奇怪仪器尖鸣，像有人在偷拍日常。",
    },
    "junko": {
        "name": "鹿目询子",
        "aliases": ["询子", "Junko", "円的母亲", "鹿目询子"],
        "work": "魔法少女小圆",
        "year": 2011,
        "age_note": "外表很年轻（人妻/母亲）",
        "accent": "#e8a0b8",
        "blurb": "鹿目圆的母亲，年轻漂亮的职场人妻，温柔时髦，妈妈脸杀伤力极高。",
        "work_intro": "《魔法少女小圆》：颠覆魔法少女的作品。鹿目询子是女主鹿目圆的母亲，以「年轻性感又温柔的妈妈」造型深入人心。",
        "appearance": "浅发短整或微卷；淡妆利落；身形高挑曲线好；常穿干练OL或居家便装；笑时温柔，烟与红酒是成人符号。",
        "intro": (
            "鹿目询子是鹿目圆的母亲，魔法少女小圆里出名的「年轻温柔性感妈妈」。"
            "她时髦、会抽烟喝酒，却把母爱落得很细：接送、关心、尊重女儿的小秘密。"
            "外表像姐姐，语气却稳定包容；色气是生活感带出来的，不是表演。"
            "厨房灯一亮，职场锐气收成妈妈的温度——锋芒收进体温里。"
        ),
        "background": [
            "鹿目家主妇兼职业女性，育有圆与小女儿，夫妻关系和睦。",
            "性格开明温柔，允许自己有成人嗜好，同时认真当妈妈。",
            "造型年轻性感，是「当代人妻妈妈」审美的重要参照之一。",
        ],
        "relations": [
            "与{{user}}：开局无旧识",
            "先以轻快礼貌打招呼，像对待客人兼邻居",
            "聊到孩子会眼睛发亮；对方失礼时仍保持风度，但笑容会淡",
        ],
        "filth_seed": "魔女夜的不安梦渣：深夜醒时烟味里会混进甜腻的假糖香，像谁在窗外许愿。",
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
    exp = exp_path.read_text(encoding="utf-8")
    for cid, d in NEW.items():
        if f'"id": "{cid}"' in exp:
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
        if marker not in exp:
            raise SystemExit("expand marker missing")
        exp = exp.replace(marker, "\n" + block + marker, 1)
    exp_path.write_text(exp, encoding="utf-8")

    en_path = ROOT / "plot/enrich_intros.py"
    en = en_path.read_text(encoding="utf-8")
    for cid, d in NEW.items():
        esc = d["intro"].replace("\\", "\\\\").replace('"', '\\"')
        entry = f'    "{cid}": (\n        "{esc}"\n    ),\n'
        section = en.split("INTROS", 1)[-1].split("def load_expand", 1)[0]
        if f'"{cid}":' in section:
            pat = re.compile(rf'"{re.escape(cid)}":\s*\(\s*".*?"\s*\),', re.S)
            en, _ = pat.subn(f'"{cid}": (\n        "{esc}"\n    ),', en, count=1)
        else:
            if "\n}\n\n\ndef load_expand_module" in en:
                en = en.replace("\n}\n\n\ndef load_expand_module", "\n" + entry + "}\n\n\ndef load_expand_module", 1)
            else:
                en = en.replace("\n}\n\ndef load_expand_module", "\n" + entry + "}\n\ndef load_expand_module", 1)
    en_path.write_text(en, encoding="utf-8")

    kb_path = ROOT / "plot/kb_fix_profiles.py"
    kb = kb_path.read_text(encoding="utf-8")
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

    expand = load_mod(ROOT / "plot/expand_profiles.py", "expand_profiles")
    enrich = load_mod(ROOT / "plot/enrich_intros.py", "enrich_intros")
    kbmod = load_mod(ROOT / "plot/kb_fix_profiles.py", "kb_fix")
    old = {
        c["id"]: c
        for c in yaml.safe_load((ROOT / "plot/characters.yaml").read_text(encoding="utf-8"))["characters"]
    }

    out = []
    for c in expand.RICH:
        cid = c["id"]
        dnew = NEW.get(cid)
        intro = enrich.INTROS.get(cid) or old.get(cid, {}).get("intro") or c.get("blurb")
        appearance = kbmod.APPEARANCE.get(cid, c["appearance"])
        relations = kbmod.RELATIONS.get(cid) or old.get(cid, {}).get("relations") or ["与{{user}}：开局无旧识"]
        background, filth = c["background"], c.get("filth_seed") or ""
        if dnew:
            intro, appearance, relations, background, filth = (
                dnew["intro"],
                dnew["appearance"],
                dnew["relations"],
                dnew["background"],
                dnew["filth_seed"],
            )
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

    print("total", len(out))
    for cid, d in NEW.items():
        print(f"{d['name']}: intro={len(d['intro'])}")


if __name__ == "__main__":
    main()
