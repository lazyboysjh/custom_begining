# Task 2 实施报告

## 完成状态

- 按设计规格精确新增 50 名动画女性角色，角色目录由 150 人扩展为 200 人。
- 50 条人物记录全部逐人原创填写，未使用批量模板或占位文本。
- 50 个角色 `id` 与 50 条 `sources` 一一对应，并在批次注册表登记 `expected_count: 50`。
- 通过既有生成器生成 50 份新增世界书档案，`worldbook/角色` 总数达到 200。

## 修改文件

- `plot/character_batches/recent_anime.yaml`
  - 新增 50 条完整 `characters` 数据和 50 条 `sources` 数据。
- `plot/character_sources.yaml`
  - 注册 `recent_anime.yaml`，分类为“近年动画与高人气角色”，`expected_count: 50`。
- `scripts/test_shengtang_regressions.py`
  - 将 Task 1 遗留的新增角色旧断言 `72` 修正为 `122`；基础角色 78 人加五个批次 24+20+16+12+50，新增批次总数应为 122，总数为 200。
- `worldbook/角色/*.md`
  - 由既有 `build_worldbook_entries()` 生成与新增名单同名的 50 份档案：浜冈梓、古手川奈奈华、八奈见杏菜、烧盐柠檬、小鞠知花、志喜屋梦子、乾纱寿叶、鹿野千夏、蝶野雏、锦木千束、井之上泷奈、有马加奈、黑川茜、后藤一里、伊地知虹夏、绫濑桃、菲伦、露西、七草荠、Vivy、爱蜜莉雅、艾姬多娜、菲欧娜·福斯特、西尔维娅·舍伍德、尤贝尔、赛丽艾、帕瓦、姬野、蕾塞、米奥莉奈·伦布兰、苏莱塔·墨丘利、莉莎·霍克艾、娜美、大和、井上织姬、朽木露琪亚、四枫院夜一、卯之花烈、照美冥、小南、珠世、甘露寺蜜璃、家入硝子、禅院真希、钉崎野蔷薇、皮克·芬格尔、阿尼·利昂纳德、月咏、丽贝卡、草薙素子。
- `.superpowers/sdd/task-2-report.md`
  - 本报告。

## 数据与来源策略

- 角色结构遵循 `plot/character_batches/anime_game.yaml`：至少 3 个无冲突别名、可识别外貌、作品和年份、人物矛盾、作品简介、至少 3 条背景、独立污秽钩子、至少 3 条关系与独立色值。
- 所有 `intro` 均以汉字计数校验，最短为 159 个汉字，高于 120 汉字要求。
- 第一条关系严格为 `与{{user}}：开局无旧识`；未新增 `age`、`age_note` 或统一年龄规则。
- 来源优先使用动画制作委员会、版权方或作品官方站：`grandblue-anime.com`、`makeine-anime.com`、`bisquedoll-anime.com`、`aonohako-anime.com`、`lycoris-recoil.com`、`ichigoproduction.com`、`bocchi.rocks`、`anime-dandadan.com`、`frieren-anime.jp`、`cyberpunk.net`、`yofukashi-no-uta.com`、`vivy-portal.com`、`re-zero.com`、`spy-family.net`、`chainsawman.dog`、`g-witch.net`、`hagaren.jp`、`one-piece.com`、`bleach-anime.com`、`naruto-official.com`、`kimetsu.com`、`jujutsukaisen.jp`、`shingeki.tv`、`bn-pictures.co.jp`、`theghostintheshell.jp`。
- 同作品角色可共用官方角色总页，但每个 `id` 均保留独立来源项与独立 `notes`。`notes` 逐条声明采用的动画季度、电影或连续性，并限制对关系、外貌、口吻和能力的合理归纳。
- 对版本冲突采用单一锚点：莉莎使用 2009 年《FULLMETAL ALCHEMIST》；草薙素子使用 1995 年押井守剧场版；角色资料不混入 SAC、ARISE、2003 年钢炼或游戏路线。

## TDD 与测试记录

实施前红灯：

```powershell
python -m unittest scripts.test_shengtang_regressions.CharacterCatalogTests
```

```text
FAIL: test_roster_has_exactly_200_unique_characters
AssertionError: 150 != 200
FAIL: test_revised_ui_copy_is_present_and_obsolete_copy_is_removed
Ran 7 tests
FAILED (failures=2)
```

生产数据写入后的第一次运行：

```text
ERROR: ... worldbook/角色/浜冈梓.md (FileNotFoundError)
FAIL: test_new_batches_have_complete_source_records
AssertionError: 122 != 72
Ran 7 tests
FAILED (failures=1, errors=1)
```

根因是新增档案尚未由既有生成器输出，以及 Task 1 只更新了总数 200，遗漏同一测试中的旧批次数值 72。执行：

```powershell
python -c "from build_shengtang_card import build_worldbook_entries; build_worldbook_entries()"
```

最终目录测试：

```powershell
python -m unittest scripts.test_shengtang_regressions.CharacterCatalogTests
```

```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.466s

OK
```

结构、字数与编码自检：

```text
OK characters=50 sources=50 unique_filth=50 min_intro_hanzi=159 profiles=200 utf8=ok
```

差异格式检查：

```powershell
git diff --cached --check
git diff --check
```

两条命令均无输出，退出码为 0；暂存清单为 54 个文件，未包含其他协作者的未跟踪目录。

## 自审

- [x] 精确 50 人，姓名顺序与设计规格一致。
- [x] 50 个唯一 `id`、唯一姓名，别名通过全 200 人冲突检查。
- [x] 每人至少 3 个别名、3 条背景、3 条关系，第一条关系固定。
- [x] 每人外貌可识别，intro 不少于 120 汉字，含身份、经历、性格矛盾、行动方式和口吻。
- [x] 每人有作品简介、独立 `filth_seed` 与 `accent`，50 个钩子文本互不重复。
- [x] 50 个来源与角色 `id` 集合严格相等，全部含 `category`、`primary`、`notes`。
- [x] 未新增年龄字段或年龄规则。
- [x] 新增 YAML、注册表及 200 份世界书均可按 UTF-8 解码。
- [x] 未触碰 `.codex/`、`.superpowers/brainstorm/`、`dist/`、`tmp/` 等其他协作者未跟踪内容。

## 资料疑点与边界

- NARUTO 官方站没有为照美冥、小南提供与新番站同粒度的稳定单角色资料页，因此使用官方《疾风传》作品／集数页，具体能力和关系限于动画正片，并在各自 notes 说明。
- 《蓝箱》《莉可丽丝》《胆大党》《BLEACH》《鬼灭之刃》《进击的巨人》等官方站以动态角色总页承载多角色，URL 不总提供稳定单角色锚点；仍为版权方官方页，未用百科替代主来源。
- 蕾塞的正式动画角色页来自 2025 年剧场版，但 `year: 2022` 按批次 schema 记录《电锯人》动画系列首播年份；notes 明确人物采用剧场版版本。
- 中文姓名沿用设计规格指定译名，日文官方名与罗马字写入别名，避免自行替换用户给定名称。
