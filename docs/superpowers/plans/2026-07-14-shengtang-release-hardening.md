# 圣堂初遇整卡修复与发布审查 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复开场卡死、封面残留、状态栏错层和模板污染，并建立可阻断发布的整卡审查闭环。

**Architecture:** 以 `plot/`、`worldbook/` 和本地构建器为唯一来源；开场生成采用带 `generation_id` 的事务式提交，仅成功时一次性覆盖 0 楼正文与 MVU data；状态栏按所在楼层事件驱动读取。卡内脚本、正则和世界书由白名单生成。

**Tech Stack:** Python 3、原生 HTML/CSS/JavaScript、SillyTavern 酒馆助手 API、MVU、Playwright、unittest。

---

### Task 1: 建立阻断式回归检查

**Files:**
- Create: `scripts/test_shengtang_regressions.py`
- Modify: `tmp/pre_release_check.py`
- Modify: `scripts/superpower_shengtang_review.py`

- [ ] 检查卡内不得出现 `大魏芳华`、`mnx`、`dawei` 等模板残留。
- [ ] 检查开场不得调用 `deleteChatMessages`、不得流式改写 0 楼、不得使用 `refresh: "all"`。
- [ ] 检查开场必须设置并过滤 `generation_id`，超时和 `pagehide` 必须调用 `stopGenerationById`。
- [ ] 检查成功提交同时包含 0 楼 `message` 与 `data`，失败路径不写楼。
- [ ] 检查状态栏不得永久 `setInterval`，必须在 `pagehide` 停止事件监听。
- [ ] 检查发布脚本存在 ERR 时返回非零退出码。
- [ ] 运行 `python scripts/test_shengtang_regressions.py`，确认当前实现按预期失败。

### Task 2: 治理构建来源与模板污染

**Files:**
- Modify: `build_shengtang_card.py`
- Create: `templates/shengtang_base.json`

- [ ] 将可复现的最小卡模板纳入仓库，移除对 `E:\create\十国千娇\十国千娇.json` 的运行时依赖。
- [ ] 白名单生成 Tavern Helper 脚本，仅保留变量结构和本卡确需脚本。
- [ ] 白名单生成 7 条本卡正则，不从其他卡继承后局部修补。
- [ ] 删除“成年二次元女性”错误声明，年龄保持 `plot/characters.yaml` 原著记录。
- [ ] 连续构建两次，比较关键产物哈希一致且第二次不产生额外 diff。

### Task 3: 重写开场生成事务

**Files:**
- Modify: `src/shengtang/ui/cover/index.html`

- [ ] 使用唯一 `generation_id` 调用 `generate`。
- [ ] 流式事件只更新封面内部进度，并按 `generation_id` 过滤。
- [ ] 超时、聊天切换和 `pagehide` 调用 `stopGenerationById`。
- [ ] 在内存依次解析封面初始化 patch 和模型最终 `<UpdateVariable>`。
- [ ] 成功后以一次 `setChatMessages([{message_id: 0, message, data}], {refresh:"affected"})` 提交。
- [ ] 失败、空输出、取消不修改 0 楼和旧变量。
- [ ] 删除所有建楼、删楼和语义不一致的降级分支。

### Task 4: 修复状态栏生命周期和多端布局

**Files:**
- Modify: `src/shengtang/ui/status/index.html`
- Modify: `scripts/ui_audit_chrome.py`

- [ ] 等待 MVU 初始化和当前楼层 `stat_data`，区分 loading、empty 和 error。
- [ ] 用 `VARIABLE_UPDATE_ENDED` 驱动刷新，不使用永久轮询。
- [ ] `pagehide` 停止事件监听、动画与计时器。
- [ ] 桌面 1280×800、平板 768×1024、手机 390×844 分别截图封面第 1/3 页和展开状态栏。
- [ ] 自动检查无水平溢出、底部按钮可见、角色列表可滚动、状态栏展开内容未裁切。

### Task 5: 世界书与角色事实审查

**Files:**
- Modify: `plot/characters.yaml`
- Modify: `worldbook/02_写作与人设规则.md`
- Modify: `worldbook/03_数值影响.md`
- Generated: `worldbook/角色/*.md`

- [ ] 校验 78 个角色 ID、姓名和别名唯一性，删除跨角色错误别名和高误触短词。
- [ ] 校验原著年龄、身份、能力、主要关系和口吻；不擅自成年化。
- [ ] 保持角色速览蓝灯、详细档案绿灯、指导规则 D0，并验证递归配置。
- [ ] 数值只调整反应强度，不覆盖角色口吻、职业习惯和关系底线。

### Task 6: 重建、Superpower 发布审查与代码复核

**Files:**
- Generated: `dist/shengtang/ui/cover/index.html`
- Generated: `dist/shengtang/ui/status/index.html`
- Generated: `圣堂初遇.json`

- [ ] 运行回归检查、构建、Superpower 审查和发布前终检。
- [ ] 读取桌面/平板/手机截图，逐张确认封面与状态栏适配。
- [ ] 请求 code-reviewer 对照本计划检查未提交改动，修复 Critical/Important 问题。
- [ ] 再运行全部验证，记录浏览器酒馆实测通道不可用时的具体原因和手动验证步骤。
