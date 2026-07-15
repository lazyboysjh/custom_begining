# 圣堂初遇 200 人角色池与文案审查 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将圣堂初遇角色池扩到 200 人，并完成封面与状态栏全部用户可见文案的统一审查和发布。

**Architecture:** 新增角色使用独立 `recent_anime.yaml` 批次，通过现有 registry-loader-build 管线合并，不改动原有 150 人数据。文案修改限定在两个 UI 源文件，构建器继续负责将角色数据同步到 UI、世界书、卡片和静态发布目录。

**Tech Stack:** Python 3、PyYAML、HTML/CSS/原生 JavaScript、unittest、Chromium/Playwright、GitHub + jsDelivr。

## Global Constraints

- 最终角色数必须精确为 200，新增批次精确为 50。
- 新角色必须满足设计规格中的完整字段、原作锚点、关系边界与来源要求。
- 不新增统一年龄规则，不输出空年龄字段。
- 封面与状态栏保持现有 C2 磨砂金属视觉，不做布局重构。
- 所有生产修改遵循测试先失败、实现后通过的 TDD 顺序。
- 发布必须先推静态资源提交，再用完整 SHA 和递增版本号重建卡片并二次推送。

---

### Task 1: 为 200 人目录和新文案建立失败测试

**Files:**
- Modify: `scripts/test_shengtang_regressions.py`
- Test: `scripts/test_shengtang_regressions.py`

**Interfaces:**
- Consumes: `load_characters()`、`load_character_sources()`、`COVER`、`STATUS`。
- Produces: 200 人计数、50 人批次、旧文案清除、新文案存在的自动验收条件。

- [ ] **Step 1: 将目录断言从 150 改为 200，并新增 recent_anime 批次断言**

```python
self.assertEqual(len(CHARS), 200)
self.assertEqual(len({char["id"] for char in CHARS}), 200)
self.assertEqual(len({char["name"] for char in CHARS}), 200)
recent = yaml.safe_load((ROOT / "plot/character_batches/recent_anime.yaml").read_text(encoding="utf-8"))
self.assertEqual(len(recent["characters"]), 50)
self.assertEqual(set(recent["sources"]), {char["id"] for char in recent["characters"]})
```

- [ ] **Step 2: 新增 UI 文案测试**

```python
for obsolete in ("枢纽抽卡", "相聚一刻", "一键随机开始", "生成开局"):
    self.assertNotIn(obsolete, COVER + STATUS)
for expected in ("召来新客", "推进当前幕", "随机启程", "揭晓初遇", "正在编织初遇"):
    self.assertIn(expected, COVER + STATUS)
```

- [ ] **Step 3: 运行测试确认失败原因是目录仍为 150 且新文案不存在**

Run: `python -m unittest scripts.test_shengtang_regressions`

Expected: FAIL，包含 `150 != 200`、缺少 `recent_anime.yaml` 或新文案断言失败。

- [ ] **Step 4: 提交失败测试**

```powershell
git add scripts/test_shengtang_regressions.py
git commit -m "Test 200-character roster and revised interface copy"
```

### Task 2: 新增 50 人动画角色批次

**Files:**
- Create: `plot/character_batches/recent_anime.yaml`
- Modify: `plot/character_sources.yaml`
- Test: `scripts/test_shengtang_regressions.py`

**Interfaces:**
- Consumes: 设计规格中的精确 50 人名单及现有批次字段结构。
- Produces: `characters: list[dict]` 与 `sources: dict[id, source]`，由 `load_characters()` 自动合并。

- [ ] **Step 1: 按现有 YAML schema 写入 50 个人物记录**

每条记录使用以下完整结构，实际内容逐人按原作填写：

```yaml
- id: unique_snake_case_id
  name: 中文正式名
  aliases: [中文简称, 日文名或英文名, 原作称号]
  work: 作品正式名
  year: 动画首播年份
  appearance: 可识别发色、眼睛、服装、姿态与道具
  blurb: 一句话身份与核心矛盾
  intro: 不少于120个汉字的身份、经历、性格、行动与口吻说明
  work_intro: 作品冲突及该角色在其中的职责
  background: [原作经历锚点1, 能力或职业锚点2, 独立目标锚点3]
  filth_seed: 只解释跨界异常且不改写原作的圣堂钩子
  relations:
  - 与{{user}}：开局无旧识
  - 原作关系锚点1
  - 原作关系锚点2
  accent: '#RRGGBB'
```

- [ ] **Step 2: 为 50 个 id 写入一一对应来源**

```yaml
sources:
  unique_snake_case_id:
    category: 动画
    primary:
    - 官方角色页或官方作品页URL
    secondary: []
    notes: 说明采用版本、时间点及必要推导边界
```

- [ ] **Step 3: 在 registry 注册批次**

```yaml
- path: recent_anime.yaml
  category: 近年动画与高人气角色
  expected_count: 50
```

- [ ] **Step 4: 运行目录测试并修复任何重复 id、姓名、别名或资料缺口**

Run: `python -m unittest scripts.test_shengtang_regressions.CharacterCatalogTests`

Expected: PASS，200 个唯一角色、50 个新增来源全部对齐。

- [ ] **Step 5: 提交角色批次**

```powershell
git add plot/character_batches/recent_anime.yaml plot/character_sources.yaml
git commit -m "Add 50 popular anime characters to Sanctum roster"
```

### Task 3: 重写封面与状态栏用户文案

**Files:**
- Modify: `src/shengtang/ui/cover/index.html`
- Modify: `src/shengtang/ui/status/index.html`
- Test: `scripts/test_shengtang_regressions.py`

**Interfaces:**
- Consumes: 设计规格的文案替换表。
- Produces: 不含内部术语和抽卡术语的 C2 封面与状态栏。

- [ ] **Step 1: 修改封面首屏、能力页、揭晓页及状态反馈文案**

应用精确目标词：`开始初遇`、`随机启程`、`揭晓初遇`、`来客将至`、`正在编织初遇`、`返回重选`。

- [ ] **Step 2: 修改状态栏字段与命令文案**

应用精确目标词：`召来新客`、`推进当前幕`、`正在续写当前幕`、`此刻尚无来客。`、`切换来客`、`篇章 / 氛围 / 场所 / 能力`、`此刻 / 所求 / 观感 / 界限 / 异象`。

- [ ] **Step 3: 保持事件 id 和行为不变，只改用户可见字符串、title 与 aria-label**

`btnDraw` 仍调用 `onDrawEncounter`；`btnTogether` 仍调用多人共同推进；生成事务、MVU 路径和 API 参数不改。

- [ ] **Step 4: 运行 UI 文案测试**

Run: `python -m unittest scripts.test_shengtang_regressions`

Expected: PASS，旧文案均不存在，新文案均存在。

- [ ] **Step 5: 提交文案改版**

```powershell
git add src/shengtang/ui/cover/index.html src/shengtang/ui/status/index.html scripts/test_shengtang_regressions.py
git commit -m "Refine Sanctum cover and status copy"
```

### Task 4: 构建并执行完整审查

**Files:**
- Modify: `build_shengtang_card.py`
- Generate: `worldbook/角色/*.md`
- Generate: `圣堂初遇.json`
- Generate: `dist/shengtang/ui/cover/index.html`
- Generate: `dist/shengtang/ui/status/index.html`

**Interfaces:**
- Consumes: 200 人目录与新 UI 源文件。
- Produces: 可导入卡、200 份角色档案及静态页面。

- [ ] **Step 1: 将卡片说明中的固定 150 改为动态角色数或 200**

`build_shengtang_card.py` 不再在描述中保留 `150名`。

- [ ] **Step 2: 构建全部产物**

Run: `python build_shengtang_card.py`

Expected: 输出 `synced cover data: 30 story types, 200 characters` 与 `synced status roster: 200`。

- [ ] **Step 3: 运行全量回归和 Superpower 审查**

```powershell
python -m unittest scripts.test_shengtang_regressions
python scripts/superpower_shengtang_review.py
git diff --check
```

Expected: 0 failures，整卡审查 ERR=0，diff check 无输出。

- [ ] **Step 4: 浏览器审查三个视口的封面、揭晓页和状态栏**

Run: `node tmp/playwright-audit/audit-c2.cjs`

Expected: desktop/tablet/phone 共 9 个 surface 均 `documentOverflow=false`、`clippedControls=[]`、`offscreenControls=[]`、`errors=[]`，生成事务 `committed=true`。

- [ ] **Step 5: 提交构建产物**

仅暂存本次相关源码、批次、世界书、新测试、两个 dist 页面和 `圣堂初遇.json`，不暂存 `.codex`、`.superpowers`、`tmp` 或其他无关 `dist`。

### Task 5: 两段式发布与 CDN 固定

**Files:**
- Modify: `圣堂初遇.json`

**Interfaces:**
- Consumes: 静态资源提交完整 SHA。
- Produces: 固定到不可变提交且缓存版本递增的交付卡。

- [ ] **Step 1: 推送包含静态页面的提交到 `origin/main`**

Run: `git push origin main`

Expected: 非 force push 成功。

- [ ] **Step 2: 用静态提交完整 SHA 和 `ST_CDN_V=9` 重建卡片**

```powershell
$env:ST_CDN_REF = git rev-parse HEAD
$env:ST_CDN_V = '9'
python build_shengtang_card.py
```

- [ ] **Step 3: 验证封面和状态栏 URL 均含相同完整 SHA 与 `?v=9`**

Run: `rg -o "custom_begining@[0-9a-f]{40}/dist/shengtang/ui/(cover|status)/index\\.html\\?v=9" 圣堂初遇.json`

Expected: cover 与 status 各出现一条。

- [ ] **Step 4: 提交并推送 CDN 固定卡**

```powershell
git add 圣堂初遇.json
git commit -m "Pin 200-character Sanctum card CDN"
git pull --rebase origin main
git push origin main
```

- [ ] **Step 5: 执行发布终审**

```powershell
python tmp/release_audit.py --require-published
python tmp/pre_release_check.py
python tmp/check_cdn_now.py
git rev-list --left-right --count HEAD...origin/main
```

Expected: 两个发布审查 ERR=0，三个 CDN 入口返回 200，ahead/behind 为 `0 0`。
