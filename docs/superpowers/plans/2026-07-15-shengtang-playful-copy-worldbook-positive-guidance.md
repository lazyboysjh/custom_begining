# 圣堂萌系文案与世界书正向引导 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将封面/状态栏操作文案改为轻松萌系，并把世界书的批量负向禁令改成可执行的正向行为锚点。

**Architecture:** 修改源码模板与核心世界书，再由 `build_shengtang_card.py` 同步 200 个角色条目、前端构建产物和整卡 JSON。测试从最终源码与生成物同时验证文案、配置和提示词结构。

**Tech Stack:** Python 3、unittest、YAML/Markdown、原生 HTML/CSS/JavaScript、SillyTavern MVU。

## Global Constraints

- 保持角色目录准确为 200 人。
- 保持 MVU `世界.出场角色` 数组与 `角色` record 的多角色语义。
- 用户可见文案不得出现内部实现术语。
- 世界书优先使用“目标行为 + 判断依据 + 可观察动作”的正向指令。
- 静态资源提交推送后，卡片 CDN 固定绑定该完整 commit SHA。

---

### Task 1: 建立文案与正向提示词回归门槛

**Files:**
- Modify: `scripts/test_shengtang_regressions.py`

**Interfaces:**
- Consumes: 封面、状态栏、核心世界书和角色生成模板文本。
- Produces: 萌系文案与正向提示词的失败断言。

- [ ] **Step 1: 写入失败测试**

断言新按钮 `开始召唤啦~`、`命运随便摇~`、`看看谁来啦`、`再摇一位~`、`故事继续走~` 存在；断言角色条目使用 `演绎锚点`，核心规则不再使用连续的 `禁止/不得/不可违背` 标题式禁令。

- [ ] **Step 2: 运行测试确认 RED**

Run: `python -m unittest scripts.test_shengtang_regressions`

Expected: FAIL，缺少萌系文案或仍命中旧负向模板。

- [ ] **Step 3: 提交测试**

```powershell
git add scripts/test_shengtang_regressions.py
git commit -m "Test playful Sanctum copy and positive guidance"
```

### Task 2: 实现萌系界面文案

**Files:**
- Modify: `src/shengtang/ui/cover/index.html`
- Modify: `src/shengtang/ui/status/index.html`

**Interfaces:**
- Consumes: 现有按钮事件、生成状态和状态栏动作。
- Produces: 保持事件不变的新用户文案。

- [ ] **Step 1: 替换操作与加载文案**

封面使用 `开始召唤啦~`、`命运随便摇~`、`看看谁来啦`、`再想一下`；状态栏使用 `再摇一位~`、`故事继续走~`、`看看其他人`。错误提示继续使用清晰陈述句。

- [ ] **Step 2: 运行目标测试确认文案 GREEN**

Run: `python -m unittest scripts.test_shengtang_regressions`

Expected: 世界书相关断言仍失败，文案断言通过。

- [ ] **Step 3: 提交界面文案**

```powershell
git add src/shengtang/ui/cover/index.html src/shengtang/ui/status/index.html
git commit -m "Make Sanctum actions playful"
```

### Task 3: 正向改写世界书规则与角色模板

**Files:**
- Modify: `worldbook/00_世界观.md`
- Modify: `worldbook/02_写作与人设规则.md`
- Modify: `worldbook/03_数值影响.md`
- Modify: `build_shengtang_card.py`

**Interfaces:**
- Consumes: 200 人角色源数据和现有世界书注入配置。
- Produces: `演绎锚点`角色模板与正向全局规则。

- [ ] **Step 1: 改写核心世界书**

把负向禁令改为明确的正向行为、证据要求与角色反应；保留“开局无旧识”“关系变化需有事件”等事实约束。

- [ ] **Step 2: 改写统一角色模板**

将 `不可违背` 改为 `演绎锚点`，以可辨识口吻、独立目标、事实评价和关系事件为正向锚点。

- [ ] **Step 3: 构建全部生成物**

Run: `python build_shengtang_card.py`

Expected: 200 个角色条目、封面/状态栏产物和 `圣堂初遇.json` 同步成功。

- [ ] **Step 4: 运行测试确认 GREEN**

Run: `python -m unittest scripts.test_shengtang_regressions`

Expected: PASS，0 failures。

- [ ] **Step 5: 提交世界书改写**

```powershell
git add build_shengtang_card.py worldbook src/shengtang/ui dist/shengtang/ui 圣堂初遇.json
git commit -m "Guide Sanctum characters with positive prompts"
```

### Task 4: 发布与固定 CDN

**Files:**
- Modify: `圣堂初遇.json`

**Interfaces:**
- Consumes: 已推送的静态资源 commit SHA。
- Produces: 使用 `ST_CDN_REF` 和新版 `ST_CDN_V` 的发布卡片。

- [ ] **Step 1: 运行整卡与浏览器审查**

Run: `python scripts/superpower_shengtang_review.py`

Run: `node tmp/playwright-audit/audit-c2.cjs`

Expected: 除发布前旧 CDN 指向外无错误；桌面、平板、手机共 9 个界面状态通过。

- [ ] **Step 2: 推送静态提交并固定 CDN**

```powershell
git push origin main
$env:ST_CDN_REF = (git rev-parse HEAD)
$env:ST_CDN_V = '9'
python build_shengtang_card.py
```

- [ ] **Step 3: 提交并推送 CDN 卡片**

```powershell
git add 圣堂初遇.json
git commit -m "Pin playful Sanctum card CDN"
git push origin main
```

- [ ] **Step 4: 发布复核**

Run: `python scripts/superpower_shengtang_review.py`

Run: `python tmp/release_audit.py --require-published`

Expected: ERR=0，远端 ahead/behind 为 `0 0`，CDN 文件 HTTP 200。

