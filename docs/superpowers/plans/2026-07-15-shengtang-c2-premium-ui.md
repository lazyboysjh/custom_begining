# 圣堂初遇 C2 高级玻璃界面 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将已确认的 C2 现代玻璃与实体金属按钮方案完整应用到封面和多角色状态栏，并完成跨端、文案和固定 CDN 发布审查。

**Architecture:** 保留现有单文件 HTML 和全部业务 JavaScript，只替换共享视觉 token、CSS 覆盖层和少量用户可见文案。封面与状态栏使用同名 `--st-*` token 和一致的按钮状态；现有 MVU、生成事务和多角色数据流不改动。

**Tech Stack:** HTML、CSS、原生 JavaScript、Python `unittest`、MVU、jsDelivr 固定 commit CDN。

## Global Constraints

- 不改变开局事务、生成流程、MVU 多角色结构和变量更新规则。
- 正式界面禁止显示 CDN、commit、版本、MVU、API、变量路径、楼层号和内部初始化过程。
- 不使用 `vh`，不产生页面横向溢出或双层滚动。
- 覆盖 360px 手机、768px 平板和 1280px 桌面；支持 `prefers-reduced-motion`。
- 按钮必须覆盖默认、悬停、按压、选中、禁用、加载和键盘焦点状态。

---

### Task 1: C2 视觉与文案阻断测试

**Files:**
- Modify: `scripts/test_shengtang_regressions.py`
- Test: `scripts/test_shengtang_regressions.py`

**Interfaces:**
- Consumes: `COVER`、`STATUS` HTML 源码常量。
- Produces: C2 token、按钮状态、响应式断点和禁用文案的发布阻断测试。

- [ ] **Step 1: 写入失败测试**

新增测试，要求封面和状态栏同时包含 `--st-btn-bg`、`--st-btn-edge`、`--st-btn-shadow`、`:focus-visible`、`:disabled`、`@media (max-width: 760px)`，并禁止 `MVU`、`API`、`CDN`、`变量初始化` 出现在用户可见 HTML 标签文本中。

- [ ] **Step 2: 运行测试确认旧样式失败**

Run: `python -m unittest scripts.test_shengtang_regressions.ProductUiTests -v`

Expected: FAIL，提示缺少 C2 按钮 token 或状态。

- [ ] **Step 3: 测试保持失败并进入最小实现**

不得降低断言强度；生产 CSS 完成后由 Task 2 和 Task 3 转绿。

### Task 2: 封面 C2 完整视觉层

**Files:**
- Modify: `src/shengtang/ui/cover/index.html`
- Test: `scripts/test_shengtang_regressions.py`

**Interfaces:**
- Consumes: 现有 `.app`、`.hero-glass`、`.panel`、`.btn`、`.mode-card`、`.char-card`、`.tab`、`.foot` DOM。
- Produces: 封面统一玻璃外壳、实体按钮、卡片、输入框、底栏和三端布局。

- [ ] **Step 1: 扩展共享 token**

在 `:root` 增加按钮表面、边缘、顶部反射、底部暗边、外阴影和选中态 token。

- [ ] **Step 2: 重写封面控件表面**

为按钮、标签页、模式卡、角色卡、输入框和面板提供外边框、顶部高光、底部暗边、悬停上浮、按压下沉、焦点环、禁用和加载状态。

- [ ] **Step 3: 清理用户文案**

将“正在初始化变量并请求模型生成”等内部过程替换为“正在准备开局，请稍候”；删除无法指导用户操作的开发式提示。

- [ ] **Step 4: 完成封面三端规则**

在 760px 和 480px 断点调整双栏、卡片网格、底栏与触控尺寸，确保无横向溢出和嵌套滚动。

- [ ] **Step 5: 运行 ProductUiTests**

Run: `python -m unittest scripts.test_shengtang_regressions.ProductUiTests -v`

Expected: 状态栏相关新增断言仍失败，封面断言通过。

### Task 3: 状态栏 C2 完整视觉层

**Files:**
- Modify: `src/shengtang/ui/status/index.html`
- Test: `scripts/test_shengtang_regressions.py`

**Interfaces:**
- Consumes: 现有 `.status-shell`、`.icon-btn`、`.role-chip`、`.metric`、`.action-btn` 和多角色渲染逻辑。
- Produces: 与封面一致的玻璃外壳、实体按钮、角色切换器、内凹数值槽和响应式布局。

- [ ] **Step 1: 同步共享 token 与按钮状态**

使用与封面同名同值的 C2 token，覆盖默认、悬停、按压、选中、禁用、加载和键盘焦点。

- [ ] **Step 2: 重做角色与指标表面**

角色切换器使用实体玻璃边缘和当前角色指示点；指标采用内凹槽与低噪声香槟金进度线。

- [ ] **Step 3: 完成状态栏三端规则**

桌面紧凑双栏，平板自动降级，手机单列并保持角色横向切换和 40px 触控目标。

- [ ] **Step 4: 清理状态文案**

空、加载、错误状态只保留“正在读取状态”“当前场景暂无角色”“状态暂不可用”等用户可理解文本。

- [ ] **Step 5: 运行完整回归**

Run: `python scripts/test_shengtang_regressions.py`

Expected: 全部测试通过且无错误。

### Task 4: 浏览器审查与固定 CDN 发布

**Files:**
- Modify: `scripts/superpower_shengtang_review.py`
- Modify: `圣堂初遇.json`
- Generate: `dist/shengtang/ui/cover/index.html`
- Generate: `dist/shengtang/ui/status/index.html`

**Interfaces:**
- Consumes: 完成的封面、状态栏和现有构建脚本。
- Produces: 已推送静态 commit、固定该 commit 的最新角色卡和发布证据。

- [ ] **Step 1: 扩展整卡审查**

增加共享 C2 token、按钮状态、禁止文案和多端断点检查。

- [ ] **Step 2: 生成静态文件并验证**

Run: `npm.cmd run copy:shengtang`

Expected: `copied cover`、`copied status`，源文件与 dist 哈希一致。

- [ ] **Step 3: 浏览器三端审查**

在 1280px、768px、360px 检查封面所有步骤、状态栏多角色切换、按钮状态、文本重叠、横向溢出、控制台错误和 reduced-motion。

- [ ] **Step 4: 提交并推送静态资源**

提交源文件、测试、审查脚本和两个 dist HTML，推送 `main`，记录完整 commit SHA。

- [ ] **Step 5: 固定 CDN 并重建角色卡**

Run: `$env:ST_CDN_REF='<STATIC_SHA>'; $env:ST_CDN_V='14'; python build_shengtang_card.py`

Expected: 卡内封面和状态栏都指向 `<STATIC_SHA>` 且查询版本为 `14`。

- [ ] **Step 6: 最终验证、提交和推送**

Run: `python scripts/test_shengtang_regressions.py`

Run: `python scripts/superpower_shengtang_review.py`

Expected: 回归全绿，审查 `ERR=0`，固定 CDN 返回 HTTP 200；提交角色卡并推送 `main`。
