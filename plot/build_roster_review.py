# -*- coding: utf-8 -*-
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
chars = yaml.safe_load((ROOT / "plot/characters.yaml").read_text(encoding="utf-8"))["characters"]
lines = [
    "# 圣堂初遇 · 角色池文案审查（40人）",
    "",
    "> 请直接批注要改的人名与字段。全部按成年处理；尽量一部一人。",
    "",
    "## 新增 15 人（近年向）",
    "星野爱、伊蕾娜、阿尔法、车海音、桐子、冥冥、公主火华、西尔维娅·洛芙、碎蜂、綾瀬星江、渡我被身子、新岛冴、艾丝妲妮雅、莱莎琳·斯托特、真希波·真理",
    "",
]
for i, c in enumerate(chars, 1):
    lines += [
        f"## {i}. {c['name']}（{c['work']} · {c.get('year', '')}）",
        f"- 别名：{'、'.join(str(a) for a in c.get('aliases') or [])}",
        f"- 一句话：{c.get('blurb', '')}",
        f"- 作品简介：{c.get('work_intro', '')}",
        f"- 外貌：{c.get('appearance', '')}",
        "- 设定要点：",
    ]
    for b in c.get("background") or []:
        lines.append(f"  - {b}")
    lines += [f"- 污秽种子：{c.get('filth_seed', '')}", ""]

out = ROOT / "plot/文案审查_角色池40.md"
out.write_text("\n".join(lines), encoding="utf-8")
print("chars", len(chars), "->", out)
